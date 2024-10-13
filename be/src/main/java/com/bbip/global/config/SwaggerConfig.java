package com.bbip.global.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI OpenAPI() {

        SecurityScheme accessToken = new SecurityScheme()
                .type(SecurityScheme.Type.APIKEY)
                .in(SecurityScheme.In.HEADER)
                .name("Authorization");

        SecurityRequirement securityRequirement = new SecurityRequirement()
                .addList("Authorization");

//        Server HttpsServer = new Server();
//        HttpsServer.setUrl("https://i11a203.p.ssafy.io/api");
//        Server HttpServer = new Server();
//        HttpServer.setUrl("http://i11a203.p.ssafy.io/api");
        Server localServer = new Server();
        localServer.setUrl("http://localhost:8080");

        return new OpenAPI()
                .components(new Components().addSecuritySchemes("Authorization", accessToken))
//                .components(new Components())
                .info(apiInfo())
                .servers(List.of(
                        localServer
                ))
                .addSecurityItem(securityRequirement)
                ;
    }

    private Info apiInfo() {
        return new Info()
                .title("BBIP API")
                .description("<h3>BBIP : Broadcasting Blur Image Processor의 Restful API입니다.</h3>")
                .version("1.0.0");
    }

}
