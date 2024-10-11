package com.bbip.domain.video.service;

import com.bbip.global.util.RedisUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.connection.Message;
import org.springframework.data.redis.listener.KeyExpirationEventMessageListener;
import org.springframework.data.redis.listener.RedisMessageListenerContainer;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.io.File;
import java.util.Set;

@Service
@Slf4j
public class RedisKeyExpirationListener extends KeyExpirationEventMessageListener {

    @Autowired
    private RedisUtil redisUtil;

    public RedisKeyExpirationListener(RedisMessageListenerContainer listenerContainer) {
        super(listenerContainer);
    }

    @Override
    public void onMessage(Message message, byte[] pattern) {

        String expiredKey = message.toString();
        String[] path = expiredKey.split("\\\\");

        if (path.length > 2) {
            deleteFile(expiredKey);
        }
    }

    @Scheduled(fixedRate = 86400000)    // 하루에 한번 실행
    public void checkAndDeleteExpiredFiles() {
        Set<String> keys = redisUtil.getDataKeys("*");
        for (String key : keys) {
            if (redisUtil.getExpire(key) == -2 && key.split("/").length > 2) {
                deleteFile(key);
            }
        }
    }

    public void deleteFile(String path) {
        File file = new File(path);
        if (file.exists()) {
            file.delete();
            log.info("로컬 파일 삭제 완료 : {}", file.toString());
        }
        else log.debug("삭제하려는 파일이 존재하지 않습니다.");
    }
}
