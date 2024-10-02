package com.bbip.global.config;

import com.bbip.domain.rtmp.controller.VideoStreamHandler;
import com.bbip.domain.signalling.controller.GeneralWebSocketHandler;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
@RequiredArgsConstructor
public class WebSocketConfig implements WebSocketConfigurer {

    private final VideoStreamHandler rtmpController;
    private final GeneralWebSocketHandler generalWebSocketHandler;

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(rtmpController, "/ws/rtmps").setAllowedOrigins("*");
    }
}
