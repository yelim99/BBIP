package com.bbip.domain.face.controller;

import com.bbip.domain.face.dto.FaceDto;
import com.bbip.domain.face.service.FaceService;
import com.bbip.global.response.CommonResponse;
import com.bbip.global.response.ListResponse;
import com.bbip.global.response.SingleResponse;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/faces")
@RequiredArgsConstructor
@Slf4j
public class FaceController {

    private final FaceService faceService;

    @Operation(
            summary = "얼굴 등록",
            description = "객체속성은 \"selt\"만 설정 필요. 본인인지(true) 아닌지(false)"
    )
    @PostMapping(value = "/upload", consumes = "multipart/form-data")
    public SingleResponse<FaceDto> saveFace(
            @RequestHeader(value = "Authorization", required = true) String accessToken,
            @RequestPart("face") FaceDto face,
            @RequestPart("image") MultipartFile image) throws IOException
    {
        FaceDto savedFace = faceService.addFace(accessToken, face, image);

        return SingleResponse.<FaceDto>builder().message("얼굴 등록 완료").data(savedFace).build();
    }

    @Operation(
            summary = "본인 얼굴 조회"
    )
    @GetMapping(value = "/self")
    public SingleResponse<FaceDto> findMyFaces(
            @RequestAttribute(value = "AccessToken", required = true) String accessToken)
    {
        FaceDto selfie = faceService.findMyFace(accessToken);

        return SingleResponse.<FaceDto>builder().message("내 얼굴 조회 완료").data(selfie).build();
    }

    @Operation(
            summary = "본인을 제외한 모든 얼굴 조회"
    )
    @GetMapping
    public ListResponse<FaceDto> getAllFaces(
            @RequestAttribute(value = "AccessToken", required = true) String accessToken)
    {
        List<FaceDto> faces = faceService.findAllFaces(accessToken);

        return ListResponse.<FaceDto>builder().dataList(faces).build();
    }

    @Operation(
            summary = "얼굴 삭제",
            description = "해당 얼굴의 id값을 PathVariable로 입력"
    )
    @DeleteMapping(value = "/{id}")
    public CommonResponse deleteFace(
            @RequestAttribute(value = "AccessToken", required = true) String accessToken,
            @PathVariable("id") Integer id)
    {
        faceService.removeFace(id);

        return new CommonResponse(id + "번 얼굴 삭제 완료");
    }
}
