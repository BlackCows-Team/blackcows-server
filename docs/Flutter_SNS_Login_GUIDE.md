# 🚀 Flutter SNS 로그인 통합 가이드

## 📋 개요
백엔드에서 SNS 로그인 API를 구현했으므로, Flutter 앱에서 다음과 같이 연동할 수 있습니다.

## 🔧 Flutter 패키지 설치

### pubspec.yaml에 추가
```yaml
dependencies:
  # HTTP 통신
  http: ^1.1.0
  dio: ^5.3.2  # 또는 http 패키지 사용
  
  # SNS 로그인 패키지들
  google_sign_in: ^6.1.5
  sign_in_with_apple: ^5.0.0
  kakao_flutter_sdk: ^1.6.1
  flutter_naver_login: ^1.8.0
  
  # 상태관리 (선택)
  provider: ^6.0.5
  # 또는 riverpod, bloc 등
```

## 🌐 SNS 로그인 Flutter 구현

### 1. Google 로그인
```dart
import 'package:google_sign_in/google_sign_in.dart';

class GoogleAuthService {
  static final GoogleSignIn _googleSignIn = GoogleSignIn(
    scopes: ['email', 'profile'],
  );
  
  static Future<Map<String, String>?> signIn() async {
    try {
      final GoogleSignInAccount? account = await _googleSignIn.signIn();
      if (account == null) return null;
      
      final GoogleSignInAuthentication auth = await account.authentication;
      
      return {
        'access_token': auth.accessToken!,
        'id_token': auth.idToken!,
      };
    } catch (e) {
      print('Google 로그인 오류: $e');
      return null;
    }
  }
}
```

### 2. Apple 로그인
```dart
import 'package:sign_in_with_apple/sign_in_with_apple.dart';

class AppleAuthService {
  static Future<String?> signIn() async {
    try {
      final credential = await SignInWithApple.getAppleIDCredential(
        scopes: [
          AppleIDAuthorizationScopes.email,
          AppleIDAuthorizationScopes.fullName,
        ],
      );
      
      return credential.identityToken; // ID 토큰 반환
    } catch (e) {
      print('Apple 로그인 오류: $e');
      return null;
    }
  }
}
```

### 3. Kakao 로그인
```dart
import 'package:kakao_flutter_sdk/kakao_flutter_sdk.dart';

class KakaoAuthService {
  static Future<String?> signIn() async {
    try {
      OAuthToken token;
      if (await isKakaoTalkInstalled()) {
        token = await UserApi.instance.loginWithKakaoTalk();
      } else {
        token = await UserApi.instance.loginWithKakaoAccount();
      }
      
      return token.accessToken;
    } catch (e) {
      print('Kakao 로그인 오류: $e');
      return null;
    }
  }
}
```

### 4. Naver 로그인
```dart
import 'package:flutter_naver_login/flutter_naver_login.dart';

class NaverAuthService {
  static Future<String?> signIn() async {
    try {
      final NaverLoginResult result = await FlutterNaverLogin.logIn();
      if (result.status == NaverLoginStatus.loggedIn) {
        return result.accessToken?.accessToken;
      }
      return null;
    } catch (e) {
      print('Naver 로그인 오류: $e');
      return null;
    }
  }
}
```

## 🔗 백엔드 API 호출

### API 서비스 클래스
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthApiService {
  static const String baseUrl = 'https://your-api-domain.com';
  
  // SNS 로그인/회원가입
  static Future<Map<String, dynamic>?> socialLogin({
    required String authType,
    required String accessToken,
    String? idToken,
    String? farmNickname,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/social-login'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'auth_type': authType,
          'access_token': accessToken,
          if (idToken != null) 'id_token': idToken,
          if (farmNickname != null) 'farm_nickname': farmNickname,
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        print('SNS 로그인 실패: ${response.body}');
        return null;
      }
    } catch (e) {
      print('API 호출 오류: $e');
      return null;
    }
  }
  
  // 일반 로그인
  static Future<Map<String, dynamic>?> emailLogin({
    required String userId,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'user_id': userId,
          'password': password,
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        print('로그인 실패: ${response.body}');
        return null;
      }
    } catch (e) {
      print('API 호출 오류: $e');
      return null;
    }
  }
}
```

## 📱 Flutter UI 구현 예시

### 로그인 화면
```dart
class LoginScreen extends StatelessWidget {
  // Google 로그인 처리
  Future<void> _handleGoogleLogin() async {
    final tokens = await GoogleAuthService.signIn();
    if (tokens != null) {
      final result = await AuthApiService.socialLogin(
        authType: 'google',
        accessToken: tokens['access_token']!,
        idToken: tokens['id_token'],
      );
      
      if (result != null) {
        // 로그인 성공 처리
        _handleLoginSuccess(result);
      }
    }
  }
  
  // Apple 로그인 처리
  Future<void> _handleAppleLogin() async {
    final idToken = await AppleAuthService.signIn();
    if (idToken != null) {
      final result = await AuthApiService.socialLogin(
        authType: 'apple',
        accessToken: idToken, // Apple은 ID 토큰을 access_token으로 전달
        idToken: idToken,
      );
      
      if (result != null) {
        _handleLoginSuccess(result);
      }
    }
  }
  
  // Kakao 로그인 처리
  Future<void> _handleKakaoLogin() async {
    final accessToken = await KakaoAuthService.signIn();
    if (accessToken != null) {
      final result = await AuthApiService.socialLogin(
        authType: 'kakao',
        accessToken: accessToken,
      );
      
      if (result != null) {
        _handleLoginSuccess(result);
      }
    }
  }
  
  // Naver 로그인 처리
  Future<void> _handleNaverLogin() async {
    final accessToken = await NaverAuthService.signIn();
    if (accessToken != null) {
      final result = await AuthApiService.socialLogin(
        authType: 'naver',
        accessToken: accessToken,
      );
      
      if (result != null) {
        _handleLoginSuccess(result);
      }
    }
  }
  
  // 로그인 성공 처리
  void _handleLoginSuccess(Map<String, dynamic> result) {
    final user = result['user'];
    final isNewUser = result['is_new_user'] ?? false;
    
    if (isNewUser) {
      // 신규 사용자 - 환영 메시지 또는 추가 정보 입력 화면
      print('환영합니다! 회원가입이 완료되었습니다.');
    } else {
      // 기존 사용자 - 메인 화면으로
      print('로그인 성공!');
    }
    
    // 토큰 저장 및 메인 화면 이동
    _saveTokensAndNavigate(result);
  }
  
  void _saveTokensAndNavigate(Map<String, dynamic> result) {
    // SharedPreferences 등을 사용해서 토큰 저장
    // Navigator를 사용해서 메인 화면으로 이동
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('로그인')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            // 일반 로그인 폼
            TextField(decoration: InputDecoration(labelText: '아이디')),
            TextField(decoration: InputDecoration(labelText: '비밀번호')),
            ElevatedButton(
              onPressed: () {
                // 일반 로그인 처리
              },
              child: Text('로그인'),
            ),
            
            Divider(),
            
            // SNS 로그인 버튼들
            ElevatedButton.icon(
              onPressed: _handleGoogleLogin,
              icon: Icon(Icons.login),
              label: Text('Google로 로그인'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            ),
            
            ElevatedButton.icon(
              onPressed: _handleAppleLogin,
              icon: Icon(Icons.apple),
              label: Text('Apple로 로그인'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.black),
            ),
            
            ElevatedButton.icon(
              onPressed: _handleKakaoLogin,
              icon: Icon(Icons.chat),
              label: Text('Kakao로 로그인'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.yellow),
            ),
            
            ElevatedButton.icon(
              onPressed: _handleNaverLogin,
              icon: Icon(Icons.nature),
              label: Text('Naver로 로그인'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 🔐 보안 고려사항

### 1. 토큰 저장
```dart
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class TokenStorage {
  static const _storage = FlutterSecureStorage();
  
  // 토큰 저장 (보안 저장소 사용)
  static Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _storage.write(key: 'access_token', value: accessToken);
    await _storage.write(key: 'refresh_token', value: refreshToken);
  }
  
  // 토큰 조회
  static Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }
  
  static Future<String?> getRefreshToken() async {
    return await _storage.read(key: 'refresh_token');
  }
  
  // 토큰 삭제 (로그아웃시)
  static Future<void> clearTokens() async {
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
  }
}
```

### 2. HTTP 인터셉터 (토큰 자동 첨부)
```dart
import 'package:dio/dio.dart';

class ApiClient {
  static final Dio _dio = Dio();
  
  static void initialize() {
    _dio.options.baseUrl = 'https://your-api-domain.com';
    
    // 요청 인터셉터 (토큰 자동 첨부)
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await TokenStorage.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          // 401 오류시 토큰 갱신 시도
          if (error.response?.statusCode == 401) {
            final refreshed = await _refreshToken();
            if (refreshed) {
              // 토큰 갱신 성공시 원래 요청 재시도
              final newToken = await TokenStorage.getAccessToken();
              error.requestOptions.headers['Authorization'] = 'Bearer $newToken';
              
              final response = await _dio.fetch(error.requestOptions);
              return handler.resolve(response);
            } else {
              // 토큰 갱신 실패시 로그인 화면으로
              _handleLogout();
            }
          }
          handler.next(error);
        },
      ),
    );
  }
  
  static Future<bool> _refreshToken() async {
    try {
      final refreshToken = await TokenStorage.getRefreshToken();
      if (refreshToken == null) return false;
      
      final response = await _dio.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );
      
      if (response.statusCode == 200) {
        final newAccessToken = response.data['access_token'];
        await TokenStorage.saveTokens(
          accessToken: newAccessToken,
          refreshToken: refreshToken,
        );
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
  
  static void _handleLogout() {
    TokenStorage.clearTokens();
    // 로그인 화면으로 이동하는 로직
  }
}
```

## 🎯 사용자 상태 관리

### Provider 패턴 사용 예시
```dart
import 'package:flutter/foundation.dart';

class AuthProvider with ChangeNotifier {
  bool _isAuthenticated = false;
  Map<String, dynamic>? _user;
  
  bool get isAuthenticated => _isAuthenticated;
  Map<String, dynamic>? get user => _user;
  
  Future<void> checkAuthStatus() async {
    final token = await TokenStorage.getAccessToken();
    if (token != null) {
      // 토큰이 있으면 사용자 정보 조회
      final userInfo = await _fetchUserInfo();
      if (userInfo != null) {
        _user = userInfo;
        _isAuthenticated = true;
        notifyListeners();
      }
    }
  }
  
  Future<bool> login({
    String? userId,
    String? password,
    String? authType,
    String? accessToken,
    String? idToken,
  }) async {
    try {
      Map<String, dynamic>? result;
      
      if (authType != null && accessToken != null) {
        // SNS 로그인
        result = await AuthApiService.socialLogin(
          authType: authType,
          accessToken: accessToken,
          idToken: idToken,
        );
      } else if (userId != null && password != null) {
        // 일반 로그인
        result = await AuthApiService.emailLogin(
          userId: userId,
          password: password,
        );
      }
      
      if (result != null) {
        await TokenStorage.saveTokens(
          accessToken: result['access_token'],
          refreshToken: result['refresh_token'],
        );
        
        _user = result['user'];
        _isAuthenticated = true;
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      print('로그인 오류: $e');
      return false;
    }
  }
  
  Future<void> logout() async {
    await TokenStorage.clearTokens();
    _user = null;
    _isAuthenticated = false;
    notifyListeners();
  }
  
  Future<Map<String, dynamic>?> _fetchUserInfo() async {
    // /auth/me API 호출해서 사용자 정보 조회
    // 구현 생략...
    return null;
  }
}
```

## 🚀 앱 시작시 인증 상태 확인

### main.dart
```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
      ],
      child: MaterialApp(
        home: AuthWrapper(),
      ),
    );
  }
}

class AuthWrapper extends StatefulWidget {
  @override
  _AuthWrapperState createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  @override
  void initState() {
    super.initState();
    // 앱 시작시 인증 상태 확인
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AuthProvider>().checkAuthStatus();
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Consumer<AuthProvider>(
      builder: (context, authProvider, child) {
        if (authProvider.isAuthenticated) {
          return MainScreen(); // 메인 화면
        } else {
          return LoginScreen(); // 로그인 화면
        }
      },
    );
  }
}
```

## 📱 플랫폼별 설정

### Android (android/app/build.gradle)
```gradle
android {
    // 최소 SDK 버전 (SNS 로그인 요구사항)
    defaultConfig {
        minSdkVersion 21  // 또는 그 이상
    }
}
```

### iOS (ios/Runner/Info.plist)
```xml
<!-- Apple Sign In -->
<key>com.apple.developer.applesignin</key>
<array>
    <string>Default</string>
</array>

<!-- URL Schemes -->
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLName</key>
        <string>google</string>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>YOUR_REVERSED_CLIENT_ID</string>
        </array>
    </dict>
</array>
```

## 🔄 완전한 로그인 플로우

### 1. 앱 시작
1. `AuthProvider.checkAuthStatus()` 호출
2. 저장된 토큰 확인
3. 토큰이 있으면 `/auth/me` 호출해서 사용자 정보 확인
4. 토큰이 유효하면 메인 화면, 무효하면 로그인 화면

### 2. SNS 로그인
1. 사용자가 SNS 로그인 버튼 클릭
2. 각 플랫폼의 OAuth 인증 진행
3. 액세스 토큰 또는 ID 토큰 획득
4. 백엔드 `/auth/social-login` API 호출
5. 백엔드에서 사용자 정보 조회 및 JWT 발급
6. 토큰 저장 및 메인 화면 이동

### 3. 일반 로그인
1. 아이디/비밀번호 입력
2. 백엔드 `/auth/login` API 호출
3. JWT 토큰 발급받기
4. 토큰 저장 및 메인 화면 이동

### 4. 자동 토큰 갱신
1. API 호출시 401 오류 발생
2. 리프레시 토큰으로 새 액세스 토큰 요청
3. 성공시 원래 API 재호출, 실패시 로그인 화면 이동

## ⚠️ 주의사항

### 1. Apple 로그인
- 최초 로그인시에만 이름 정보 제공
- 사용자가 앱을 삭제 후 재설치하면 다른 social_id 발급될 수 있음
- iOS 13 이상에서만 지원

### 2. Kakao 로그인
- 카카오톡 앱이 설치되어 있으면 앱으로, 없으면 웹으로 로그인
- 비즈니스 채널 생성 필요할 수 있음

### 3. Naver 로그인
- 네이버 개발자 센터에서 앱 등록 필요
- URL Scheme 설정 필요

### 4. 보안
- 토큰은 반드시 secure storage에 저장
- API 통신은 HTTPS 사용
- 토큰 만료시 자동 갱신 로직 구현
- 로그아웃시 토큰 완전 삭제

이제 백엔드와 Flutter 앱이 완전히 연동되어 다양한 방식의 로그인을 지원할 수 있습니다! 🎉