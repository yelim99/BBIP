package com.bbip.domain.oauth.service;

import com.bbip.domain.token.service.TokenService;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;
import java.io.IOException;

@Component
@Slf4j
@RequiredArgsConstructor
public class CustomOAuth2SuccessHandler implements AuthenticationSuccessHandler {

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                                        Authentication authentication) throws IOException, ServletException {
        // 토큰 가져오기
        String accessToken = (String) request.getAttribute("accessToken");
        String refreshToken = (String) request.getAttribute("refreshToken");
//        log.info("accessToken: {} refreshToken: {}", accessToken, refreshToken);
        log.info("access token: {}", accessToken);

        // 토큰을 포함하여 Flutter로 리디렉션할 URL 생성
        String redirectUrl = "bbip://callback?accessToken=" + accessToken + "&refreshToken=" + refreshToken;

        response.sendRedirect(redirectUrl);

//        //header로 전달
//        response.addHeader("accessToken", accessToken);
//        response.addHeader("refreshToken", refreshToken);
//
//        log.info("response: {}", response.getHeader("accessToken"));
//        log.info("response: {}", response.getHeader("refreshToken"));

    }
}
