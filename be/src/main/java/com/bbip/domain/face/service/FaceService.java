package com.bbip.domain.face.service;

import com.bbip.domain.face.dto.FaceDto;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

public interface FaceService {

    FaceDto addFace(String accessToken, FaceDto face, MultipartFile image);

    List<FaceDto> findAllFaces(String accessToken);

    FaceDto findMyFace(String accessToken);

    void removeFace(Integer id);
}
