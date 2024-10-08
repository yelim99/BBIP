package com.bbip.domain.token.service;

import com.bbip.global.exception.InvalidTokenException;
import com.bbip.global.util.JwtUtil;
import com.bbip.global.util.RedisUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
@Slf4j
public class TokenServiceImpl implements TokenService {

    private final JwtUtil jwtUtil;
    private final RedisUtil redisUtil;

    /**
     * Access Token 발급
     * @param email
     * @param userId
     * @return
     */
    @Override
    public String generateAccessToken(String email, Integer userId) {
        return jwtUtil.generateToken(email, userId);
    }

    /**
     * Refresh Token 발급
     * @param email
     * @return
     */
    @Override
    public String generateRefreshToken(String email) {
        String refreshToken = jwtUtil.generateRefreshToken(email);
        long refreshTokenExpirationTime = jwtUtil.getRefreshTokenExpirationTime();

        // Redis에 Refresh Token 저장
        redisUtil.setDataExpire(email, refreshToken, refreshTokenExpirationTime);
        return refreshToken;
    }

    /**
     * Redis에서 Refresh Token 검증
     * @param email
     * @param refreshToken
     * @return
     */
    @Override
    public void validateRefreshToken(String email, String refreshToken) {
        String storedToken = redisUtil.getData(email);
        if (storedToken == null || !storedToken.equals(refreshToken))
            throw new InvalidTokenException("[엑세스토큰 발급 실패]일치하는 리프레시 토큰이 없음");
    }

    /**
     * 로그아웃 시 Refresh Token 삭제
     * @param username
     */
    @Override
    public void removeRefreshToken(String username) {
        if(redisUtil.removeData(username)) return;
        throw new InvalidTokenException("[로그아웃 실패]해당하는 토큰이 없음");
    }
}