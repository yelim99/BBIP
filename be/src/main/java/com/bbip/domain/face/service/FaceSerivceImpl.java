package com.bbip.domain.face.service;

import com.bbip.domain.face.dto.FaceDto;
import com.bbip.domain.face.entity.FaceEntity;
import com.bbip.domain.face.repository.FaceRepository;
import com.bbip.domain.user.entity.UserEntity;
import com.bbip.domain.user.repository.UserRepository;
import com.bbip.global.util.FaceUtil;
import com.bbip.global.util.JwtUtil;
import com.bbip.global.util.S3FileUploadUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class FaceSerivceImpl implements FaceService {

    private final FaceRepository faceRepository;
    private final UserRepository userRepository;
    private final S3FileUploadUtil fileUploadUtil;
    private final JwtUtil jwtUtil;
    private final FaceUtil faceUtil;

    @Override
    public FaceDto addFace(String accessToken, FaceDto face, MultipartFile image) {
        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);

        face.setUserId(userId);
        String fileName = UUID.randomUUID().toString() + image.getOriginalFilename();
        face.setFileName(fileName);
        String fileUrl = fileUploadUtil.uploadFile(image, fileName);
        face.setFileUrl(fileUrl);
        byte[] faceembedding = faceUtil.getFaceEmbeddingFromFastAPI(fileUrl);
        face.setFaceEmbedding(faceembedding);
        UserEntity userEntity = userRepository.findById(userId);
        FaceEntity faceEntity = faceRepository.save(face.toEntity(userEntity));
        log.info("얼굴 등록 완료");
        return faceEntity.toDto();
    }

    @Override
    public List<FaceDto> findAllFaces(String accessToken) {
        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);

        return faceRepository.findByUserId(userId).stream()
                .map(FaceEntity::toDto)
                .toList();
    }

    @Override
    public FaceDto findMyFace(String accessToken) {
        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);

        return faceRepository.findMineById(userId).toDto();
    }

    @Override
    public void removeFace(Integer id) {

        String fileName = faceRepository.findFileNameById(id);
        log.info("fileName : {}", fileName);
        fileUploadUtil.deleteFile(fileName);
        faceRepository.deleteById(id);
        log.info("얼굴 삭제 완료");
    }
}
