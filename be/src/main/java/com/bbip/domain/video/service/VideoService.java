package com.bbip.domain.video.service;

import org.springframework.web.multipart.MultipartFile;

public interface VideoService {
    String saveVideo(String accessToken, MultipartFile video);
}
