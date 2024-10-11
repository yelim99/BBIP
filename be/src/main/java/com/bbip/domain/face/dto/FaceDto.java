package com.bbip.domain.face.dto;

import com.bbip.domain.face.entity.FaceEntity;
import com.bbip.domain.user.entity.UserEntity;
import lombok.*;
import org.springframework.stereotype.Component;

@Component
@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FaceDto {

    private Integer id;
    private Integer userId;
    private String fileUrl;
    private String fileName;
    private byte[] faceEmbedding;
    private Boolean self;

    public FaceDto (Boolean self) {
        this.self = self;
    }

    public FaceEntity toEntity(UserEntity userEntity) {
        return FaceEntity.builder()
//                .id(id)
                .userEntity(userEntity)
                .fileUrl(fileUrl)
                .fileName(fileName)
                .self(self)
                .faceEmbedding(faceEmbedding)
                .build();
    }
}
