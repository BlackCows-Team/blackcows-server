from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import CharacterTextSplitter
from langchain.schema import Document
import os
from .types import DairyChatState, get_chat_memory, append_chat_memory

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
_vectordb = None

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = "\n".join([page.get_text() for page in doc])

    doc.close()
    return text

def extract_texts_from_folder(folder_path):
    documents = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        length_function=len,
    )

    for root, _, files in os.walk(folder_path):
        for file_name in files:
            print(file_name, "🔥")
            full_path = os.path.join(root, file_name)
            if file_name.lower().endswith(".pdf"):
                text = extract_text_from_pdf(full_path)
            elif file_name.lower().endswith(".txt"):
                with open(full_path, encoding="utf-8") as f:
                    text = f.read()
            else:
                continue

            # 텍스트를 먼저 나눠서 각 청크에 파일명 metadata 붙임
            split_texts = splitter.split_text(text)
            for i, chunk in enumerate(split_texts):
                documents.append(Document(page_content=chunk, metadata={"source": file_name}))
    return documents

def build_or_load_vectordb(source_folder: str, persist_dir: str = "RAG/chroma"):
    global _vectordb
    if _vectordb:
        print("✅ 메모리 캐시에 이미 로드된 벡터 DB 사용 중")
        return _vectordb

    embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectordb = None
    collection_path = os.path.join(persist_dir, "chroma.sqlite3")

    if not os.path.exists(collection_path):
        print("🆕 벡터 DB가 존재하지 않아 새로 생성합니다.")
        raw_documents = extract_texts_from_folder(source_folder)
        vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding)


        # === 임베딩 배치 처리 ===
        BATCH_SIZE = 100
        for i in range(0, len(raw_documents), BATCH_SIZE):
            batch = raw_documents[i:i + BATCH_SIZE]
            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]
            vectordb.add_texts(texts=texts, metadatas=metadatas)

    else:
        print("📂 기존 벡터 DB를 불러옵니다.")
        vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding)

    _vectordb = vectordb
    return vectordb



def generate_rag_response(state: DairyChatState) -> DairyChatState:
    """RAG 기반으로 낙농업에 대한 전문적인 답변을 생성하는 노드"""
    vectordb = build_or_load_vectordb("RAG/source_docs")
    memory_text = "\n".join(get_chat_memory(state["user_id"], state["chat_id"]))
    '''
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(state["current_question"])

    # 출처와 함께 context 구성 
    context = ""
    for doc in docs:
        source = doc.metadata.get("source", "알 수 없는 문서")
        context += f"[출처: {source}]\n{doc.page_content}\n\n"
    '''

    # ✅ 유사도 점수 포함 검색
    docs_with_scores: list[tuple[Document, float]] = vectordb.similarity_search_with_score(
        query=state["current_question"],
        k=3
    )

    # 출처와 점수와 함께 context 구성
    context = ""
    for doc, score in docs_with_scores:
        source = doc.metadata.get("source", "알 수 없는 문서")
        context += f"[출처: {source} | 유사도: {score:.4f}]\n{doc.page_content}\n\n"
    
    context = context.strip() or "※ 참고할 문서가 없습니다."
    print('🔍 RAG 참고 자료 확인:\n', context)

    # print('CHROMA에서 검색한 지식 확인:\n', context)
    # print('--------------------------------')

    prompt = PromptTemplate(
        input_variables=["context", "memory", "question"],
        template="""
당신은 낙농업에 특화된 챗봇 '소담이'입니다.
아래 참고 자료를 우선적으로 사용해서 답변하세요.

만약 참고 자료가 비어있거나 참고자료에서 답을 찾을 수 없다면,
당신이 알고 있는 지식이나 상식, 경험을 바탕으로 대신 답해도 괜찮습니다.
단, 정확한 답변이어야 하며, 너무 길게 설명하지 마세요.

[사용자와의 대화 기록]
{memory}

[참고 자료]
{context}

[질문]
{question}

[답변 규칙]
- 짧고 쉬운 단어를 사용하여, 한 문단 이내로 답변하세요.
- 특수기호, 이모지, 불필요한 장식은 사용하지 마세요.
- 영어로 질문하는 경우, 영어로 답변하세요.
- 출처는 마지막 줄에 반드시 포함합니다.  
    → 형식: [출처: 파일명1, 파일명2]  
    → 출처 표기 시 파일 확장자(.txt, .pdf)는 생략하세요.
"""
    )

    llm = ChatOpenAI(temperature=0.3, model="gpt-4o-mini", streaming=True, openai_api_key=OPENAI_API_KEY)
    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke({
        "context": context,
        "memory": memory_text,
        "question": state["current_question"]
    })

    append_chat_memory(state["user_id"], state["chat_id"], state["current_question"], answer)

    return {
        **state,
        "current_answer": answer
    }
