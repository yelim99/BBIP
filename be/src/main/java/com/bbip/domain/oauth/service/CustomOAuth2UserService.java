package com.bbip.domain.oauth.service;

import com.bbip.domain.token.service.TokenServiceImpl;
import com.bbip.domain.user.dto.UserDto;
import com.bbip.domain.user.service.UserServiceImpl;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

import java.util.Map;


@Service
@RequiredArgsConstructor
@Slf4j
public class CustomOAuth2UserService extends DefaultOAuth2UserService {

    private final TokenServiceImpl tokenService;
    private final UserServiceImpl userService;
    private final HttpServletRequest httpServletRequest;  // HttpServletRequest 주입

    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {

        OAuth2User oAuth2User = super.loadUser(userRequest);
        log.info("oAuth2User: {}", oAuth2User);

        Map<String, Object> attributes = oAuth2User.getAttributes();

        String email = (String) attributes.get("email");
        log.info("email: {}", email);
        String name = (String) attributes.get("name");
        log.info("name: {}", name);
        String oauthProvider = "google";

        UserDto user = userService.saveOrUpdateOAuthUser(email, name, oauthProvider);

        // JWT 및 Refresh Token 발급
        String accessToken = tokenService.generateAccessToken(email, user.getId());
        String refreshToken = tokenService.generateRefreshToken(email);

        // Redis에 Refresh Token 저장
        tokenService.generateRefreshToken(email);

        // HttpServletRequest에 토큰 저장
        httpServletRequest.setAttribute("accessToken", accessToken);
        httpServletRequest.setAttribute("refreshToken", refreshToken);

        return oAuth2User;
    }
}