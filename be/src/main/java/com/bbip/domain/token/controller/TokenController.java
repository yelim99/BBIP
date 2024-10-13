package com.bbip.domain.token.controller;
import com.bbip.domain.token.service.TokenServiceImpl;
import com.bbip.global.exception.InvalidParamException;
import com.bbip.global.response.CommonResponse;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class TokenController {

    private final TokenServiceImpl tokenService;

    /**
     * Refresh Token으로 새로운 Access Token 발급
     * @param request
     * @return
     */
    @Operation(
            summary = "엑세스 토큰 재발급",
            description = "userId, userName, refreshToken 입력 필요"
    )
    @PostMapping("/refresh-token")
    public CommonResponse refreshAccessToken(@RequestBody Map<String, String> request) {

        if (request.get("userId") == null || request.get("email") == null || request.get("refreshToken") == null) {
            throw new InvalidParamException("[매개변수 입력 오류]userId, userName, refreshToken 입력 확인 필요");
        }
        String userId = request.get("userId");
        String email = request.get("email");
        String refreshToken = request.get("refreshToken");

        // Refresh Token 검증
        tokenService.validateRefreshToken(email, refreshToken);
        String newAccessToken = tokenService.generateAccessToken(email, Integer.parseInt(userId));

        HttpHeaders header = new HttpHeaders();
        header.add("Authorization", newAccessToken);
        return new CommonResponse(header, "엑세스 토큰 재발급 완료");
    }

    /**
     * 로그아웃 시 Refresh Token 삭제
     * @param request
     * @return
     */
    @Operation(
            summary = "로그아웃",
            description = "로그아웃 시 Refresh Token 삭제하기 위한 api"
    )
    @PostMapping("/logout")
    public CommonResponse logout(@RequestBody Map<String, String> request) {

        if (request.get("userId") == null || request.get("email") == null) {
            throw new InvalidParamException("[매개변수 입력 오류]userId, email 입력 확인 필요");
        }

        // 토큰을 저장하는 키를 이메일로만 하는게 맞나,,? 구글로만 할거면 상관없지만
        String email = request.get("email");

        // Redis에서 Refresh Token 삭제
        tokenService.removeRefreshToken(email);
        return new CommonResponse("로그아웃 성공");
    }
}