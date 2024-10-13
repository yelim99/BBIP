package com.bbip.domain.video.controller;

import com.bbip.domain.video.service.VideoService;
import com.bbip.global.exception.InvalidParamException;
import com.bbip.global.response.CommonResponse;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/videos")
@Slf4j
public class VideoController {

    private final VideoService videoService;

    /**
     * 녹화된 라이브 영상을 전달받아 로컬 저장소에 임시저장하는 api
     * @param accessToken
     * @param video
     * @return
     */
    @Operation(
            summary = "라이브 녹화 영상 임시 저장"
    )
    @PostMapping(consumes = "multipart/form-data")
    public CommonResponse saveVideo(
            @RequestHeader(value = "Authorization", required = false) String accessToken,
            @RequestParam("video") MultipartFile video) {

        if (video.isEmpty()) {
            throw new InvalidParamException("비디오 파일 미입력");
        }

        videoService.saveVideo(accessToken, video);
        return new CommonResponse("비디오 임시저장 완료");
    }
}
