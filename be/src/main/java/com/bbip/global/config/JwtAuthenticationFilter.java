package com.bbip.global.config;

import com.bbip.global.util.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.ArrayList;

@Component
@RequiredArgsConstructor
@Slf4j
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        String token = jwtUtil.getJwtFromRequest(request);

        if (token != null && jwtUtil.validateToken(token)) {
            String userEmail = jwtUtil.getEmailFromJWT(token);
//            log.info("userEmail: {}", userEmail);
            // 인증 객체 생성 후 SecurityContext에 저장
            UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(userEmail, null, new ArrayList<>());
            SecurityContextHolder.getContext().setAuthentication(authentication);
        } else log.info("헤더에 토큰이 없어요");

        try{
            log.info("doFilter");
            filterChain.doFilter(request, response);
        } catch (Exception e) {
            log.error("JWT 필터에서 예외 발생", e);
        }
    }
}