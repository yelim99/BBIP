package com.bbip.global.util;

import com.fasterxml.jackson.annotation.JsonProperty;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

@Component
public class FaceUtil {

    private final WebClient webClient;

    public FaceUtil(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder.baseUrl("http://localhost:8000").build();
    }

    // FastAPI에 S3 URL을 보내고 BLOB(바이너리) 데이터를 받아오는 메서드
    public byte[] getFaceEmbeddingFromFastAPI(String imageUrl) {
        return this.webClient.post()
                .uri("/fast/process-image")
                .bodyValue(new ImageRequest(imageUrl))
                .retrieve()
                .bodyToMono(byte[].class)
                .block();  // 동기 방식으로 처리
    }

    // 이미지 URL을 FastAPI로 보내기 위한 DTO
    public static class ImageRequest {
        @JsonProperty("image_url")
        private String imageUrl;

        public ImageRequest(String imageUrl) {
            this.imageUrl = imageUrl;
        }

        public String getImageUrl() {
            return imageUrl;
        }

        public void setImageUrl(String imageUrl) {
            this.imageUrl = imageUrl;
        }
    }
}
