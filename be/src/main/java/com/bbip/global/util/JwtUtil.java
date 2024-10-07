package com.bbip.global.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.security.oauth2.jwt.JwtException;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.util.Date;

@Component
public class JwtUtil {

    private final String JWT_SECRET = "bbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbipbbip";
    private final long JWT_EXPIRATION = 3600000;  // Access Token 유효 기간, 단위:ms (1시간)
    private final long REFRESH_TOKEN_EXPIRATION = 86400;  // Refresh Token 유효 기간, 단위:s (1일)

    private static final String HEADER_STRING = "Authorization";
    private static final String TOKEN_PREFIX = "Bearer ";

    // Access Token 생성
    public String generateToken(String username, Integer userId) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + JWT_EXPIRATION);

        return Jwts.builder()
                .setSubject(username)
                .claim("userId", userId)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(SignatureAlgorithm.HS512, JWT_SECRET)
                .compact();
    }

    // Refresh Token 생성
    public String generateRefreshToken(String username) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + REFRESH_TOKEN_EXPIRATION*1000);

        return Jwts.builder()
                .setSubject(username)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(SignatureAlgorithm.HS512, JWT_SECRET)
                .compact();
    }

    // Refresh Token 만료 시간 가져오기
    public long getRefreshTokenExpirationTime() {
        return REFRESH_TOKEN_EXPIRATION;
    }

    // JWT 토큰에서 사용자 이름 추출
    public String getUsernameFromJWT(String token) {
        Claims claims = Jwts.parser()
                .setSigningKey(JWT_SECRET)
                .parseClaimsJws(token.substring(7))
                .getBody();

        return claims.getSubject();
    }

    // JWT 토큰에서 사용자 아이디 추출
    public Integer getUserIdFromJWT(String token) {
        Claims claims = Jwts.parser()
                .setSigningKey(JWT_SECRET)
                .parseClaimsJws(token)
                .getBody();

        return claims.get("userId", Integer.class);
    }

    // JWT 토큰 유효성 검사
    public boolean validateToken(String token) {
        try {
            Jwts.parser().setSigningKey(JWT_SECRET).parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    // 요청 헤더에서 JWT를 추출하는 메서드
    public String getJwtFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader(HEADER_STRING);
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith(TOKEN_PREFIX)) {
            return bearerToken.substring(7);  // "Bearer " 이후의 토큰 부분만 추출
        }
        return null;
    }
}
