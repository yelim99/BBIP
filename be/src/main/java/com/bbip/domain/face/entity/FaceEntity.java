package com.bbip.domain.face.entity;

import com.bbip.domain.face.dto.FaceDto;
import com.bbip.domain.user.entity.UserEntity;
import jakarta.persistence.*;
import lombok.*;

@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "face")
public class FaceEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column
    private Integer id;

    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    private UserEntity userEntity;

    @Column(name = "file_url", nullable = false)
    private String fileUrl;

    @Column(name = "file_name", nullable = false)
    private String fileName;

    @Lob
    @Column(name = "face_embedding", nullable = false)
    private byte[] faceEmbedding;

    @Column(nullable = false)
    private Boolean self;

    public FaceDto toDto() {
        return FaceDto.builder()
                .id(id)
                .userId(userEntity.getId())
                .fileUrl(fileUrl)
                .fileName(fileName)
                .faceEmbedding(faceEmbedding)
                .self(self)
                .build();
    }
}
