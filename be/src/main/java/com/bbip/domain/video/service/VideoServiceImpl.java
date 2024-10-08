package com.bbip.domain.video.service;

import com.bbip.global.exception.EncodingFailException;
import com.bbip.global.exception.VideoSaveFailException;
import com.bbip.global.util.JwtUtil;
import com.bbip.global.util.RedisUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

@Service
@Slf4j
@RequiredArgsConstructor
public class VideoServiceImpl implements VideoService {

    @Autowired
    private RedisUtil redisUtil;

    @Autowired
    private JwtUtil jwtUtil;

    @Value("${video.upload.dir}")
    private String uploadDir;

    @Value("${video.upload.expire-time}")
    private int expireTime;     // 1분

    @Value("${video.upload.original-file-name}")
    private String originalSubfix;

    /**
     * 입력받은 비디오 파일을 로컬 저장소에 임시 저장하는 함수
     * 저장 기간은 환경변수 ${video.upload.expire-time}에서 설정
     * @param accessToken   userId 추출을 위한 엑세스 토큰
     * @param video 사용자가 입력한 비디오
     * @return
     */
    @Override
    public String saveVideo(String accessToken, MultipartFile video) {

        // JWT토큰에서 사용자 id 추출
        int userId = jwtUtil.getUserIdFromJWT(accessToken);

        // 파일명 중복 방지를 위한 prefix 설정 : "userId_현재시간_"
        String filePrefix = String.valueOf(userId) + "_" + System.currentTimeMillis() + "_";
        String fileName = video.getOriginalFilename();  // 저장할 파일명
        File uploadDirectory = new File(uploadDir);     // 파일을 저장할 위치

        // 해당 폴더가 없으면 생성
        if (!uploadDirectory.exists()) uploadDirectory.mkdirs();

        // 업로드할 원본 파일(인코딩 전)의 경로 생성 (저장위치 + 파일이름)
        File uploadFile = new File(uploadDirectory, filePrefix + originalSubfix);
        fileSave(video, uploadFile, fileName);  // 파일 저장

        return uploadFile.toString();
    }

    /**
     * 원본파일을 우선 저장 후 해당 파일을 읽어 압축한 후 저장된 원본파일을 삭제하는 함수
     * @param video 저장할 비디오 파일
     * @param uploadFile  원본파일 저장 경로
     * @param fileName  비디오 파일 기존 이름, prefix + 기존 파일명으로 최종 저장됨
     */
    private void fileSave(MultipartFile video, File uploadFile, String fileName) {
        try {
            video.transferTo(uploadFile);                                               // 원본파일 저장
            String filePath = encodeVideoToH264(uploadFile.toString(), fileName);        // 인코딩 파일 저장
            redisUtil.setDataExpire(filePath, fileName, expireTime);                    // 인코딩 파일 경로 redis 저장
            log.info("동영상 저장 완료");
        } catch (IOException e) {
            throw new VideoSaveFailException("원본 동영상 저장 중 오류 발생");
        }

        if (uploadFile.delete()) log.info("원본파일 삭제");       // 처음에 저장한 원본파일 삭제 후 로그 출력
    }

    /**
     * 저장되어 있는 원본파일을 읽어 H.264로 압축(인코딩)해서 같은 위치에 저장하는 인코딩 함수
     * @param originalPath 원본 파일 경로
     * @param fileName 비디오 파일 기존 이름
     * @return
     */
    private String encodeVideoToH264(String originalPath, String fileName) {

        String newFilePath = originalPath.replace(originalSubfix, fileName);

        // FFmpeg 명령어
        String[] command = {
                "ffmpeg",
                "-analyzeduration", "100M",
                "-probesize", "100M",
                "-f", "mp4",
                "-i", originalPath,
                "-pix_fmt", "yuv420p",
                "-c:v", "libx264",
                "-crf", "30",
                "-movflags", "+faststart",
                "-c:a", "aac",
                "-b:a", "192k",
                newFilePath
        };

        try {
            ProcessBuilder processBuilder = new ProcessBuilder(command);
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    log.info(line);
                }
            }
            process.waitFor();
        } catch (IOException | InterruptedException e) {
            throw new EncodingFailException("녹화영상 인코딩 중 오류 발생");
        }

        return newFilePath;
    }

}
