package com.bbip.global.config;

import com.bbip.domain.oauth.service.CustomOAuth2SuccessHandler;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
@Slf4j
public class SecurityConfig {

    @Autowired
    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Autowired
    private final CustomOAuth2SuccessHandler customOAuth2SuccessHandler;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        log.info("필터 시작"+http.toString());
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(auth -> auth
//                        .requestMatchers("/", "/login", "/oauth2/**", "/api/auth/refresh-token", "/public/**", "/error").permitAll()
                        .requestMatchers("/**").permitAll()
                        .anyRequest().authenticated())
                .oauth2Login(oauth -> oauth
                        .loginPage("/login")
                        .successHandler(customOAuth2SuccessHandler))  // 성공 핸들러 설정
                .logout(logout -> logout
                        .logoutSuccessUrl("/login"))
                .exceptionHandling(ex -> ex
                        .authenticationEntryPoint((request, response, authException) -> response.sendRedirect("/login")));
        //http.addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}