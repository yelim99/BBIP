package com.bbip.global.util;

import com.amazonaws.SdkClientException;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.model.DeleteObjectRequest;
import com.amazonaws.services.s3.model.ObjectMetadata;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Service
@Slf4j
@RequiredArgsConstructor
public class S3FileUploadUtil {

    private final AmazonS3 s3Client;

    @Value("${cloud.aws.s3.bucket}")
    private String bucketName;

    private static final String defaultUrl = "https://bbip33.s3.ap-northeast-2.amazonaws.com";

    /**
     * 파일 데이터를 S3버킷에 업로드 하고 등록된 파일의 url 주소를 반환하는 메서드
     * @param file 등록할 파일 데이터
     * @return 저장된 파일의 버킷 url
     */
    public String uploadFile(MultipartFile file, String fileName) {

        try {
            s3Client.putObject(bucketName, fileName, file.getInputStream(), getObjectMetadtat(file));
            log.info("버킷에 파일 업로드 성공: " + fileName);
            return defaultUrl + "/" + fileName;
        } catch (IOException e) {
            throw new RuntimeException("파일 업로드 실패");
        }
    }

    public void deleteFile(String fileName) {

        try {
            s3Client.deleteObject(new DeleteObjectRequest(bucketName, fileName));
        } catch (SdkClientException e) {
            throw new SdkClientException("파일 삭제 실패");
        }

    }

    private ObjectMetadata getObjectMetadtat(MultipartFile file) {
        ObjectMetadata objectMetadata = new ObjectMetadata();
        objectMetadata.setContentType("image/jpeg");
        objectMetadata.setContentLength(file.getSize());
        return objectMetadata;
    }
}
