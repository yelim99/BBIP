import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_web_auth/flutter_web_auth.dart';
import 'package:uni_links/uni_links.dart';
import 'dart:async';

class LandingPage extends StatefulWidget {
  const LandingPage({super.key});

  @override
  _LandingPageState createState() => _LandingPageState();
}

class _LandingPageState extends State<LandingPage> {
  final storage = const FlutterSecureStorage(); // Secure Storage 인스턴스 생성
  StreamSubscription? _linkSubscription;

  @override
  void initState() {
    super.initState();
    _initUniLinks();
  }

  Future<void> _initUniLinks() async {
    // 초기 링크 설정
    _linkSubscription = linkStream.listen((String? link) {
      if (link != null) {
        // 콜백 URL에서 accessToken과 refreshToken 추출
        final uri = Uri.parse(link);
        final accessToken = uri.queryParameters['accessToken'];
        final refreshToken = uri.queryParameters['refreshToken'];

        print(accessToken);
        print(refreshToken);
        if (accessToken != null && refreshToken != null) {
          // Secure Storage에 토큰 저장
          storage.write(key: 'accessToken', value: accessToken);
          storage.write(key: 'refreshToken', value: refreshToken);

          print('Tokens saved in secure storage');
          Get.toNamed('/face_registration');
        } else {
          print('Token not found in the callback URL');
        }
      }
    });
  }

  @override
  void dispose() {
    _linkSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: false,
      body: Container(
        decoration: const BoxDecoration(
          image: DecorationImage(
            fit: BoxFit.cover,
            image: AssetImage('assets/wallpaper.jpg'),
          ),
        ),
        child: Stack(
          children: [
            const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    SizedBox(height: 150),
                    Text(
                      'BBIP',
                      style: TextStyle(
                        fontSize: 48,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            Align(
              alignment: Alignment.bottomCenter,
              child: Padding(
                padding: const EdgeInsets.only(bottom: 60),
                child: ElevatedButton.icon(
                  onPressed: () {
                    _signInWithGoogle(context); // Google 로그인 함수 호출
                  },
                  icon: Image.asset(
                    'assets/google_logo.png',
                    height: 24.0,
                    width: 24.0,
                  ),
                  label: const Text(
                    'Sign In with Google',
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.black,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 12),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _signInWithGoogle(BuildContext context) async {
    print('signUpWithGoogle Pressed');

    try {
      // Web Auth 플로우를 사용하여 Google 로그인 페이지로 리디렉션
      final result = await FlutterWebAuth.authenticate(
        url: 'http://j11a203.p.ssafy.io:8080/oauth2/authorization/google',
        callbackUrlScheme: 'bbip', // 이 스키마는 콜백 URL을 설정할 때 필요
      );

      // 성공적으로 로그인 후, uni_links가 처리할 수 있도록 아무 것도 하지 않음
      print('Redirecting to uni_links');
    } catch (e) {
      print('Failed to authenticate with Google: $e');
    }
  }
}
