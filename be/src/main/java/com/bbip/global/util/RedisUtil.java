package com.bbip.global.util;

import com.bbip.global.exception.InvalidTokenException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.Set;

@Component
@RequiredArgsConstructor
@Slf4j
public class RedisUtil {

    private final StringRedisTemplate redisTemplate;

    public void setData(String key, String value) {
        redisTemplate.opsForValue().set(key, value);
        log.info("set data key:{}, value:{}", key, value);
    }

    /**
     *
     * @param key
     * @param value
     * @param expirationTime 데이터 유효기간 (초 단위)
     */
    public void setDataExpire(String key, String value, long expirationTime) {
        Duration expireDuration = Duration.ofSeconds(expirationTime);
        redisTemplate.opsForValue().set(key, value, expireDuration);
        log.info("set data expire key:{}, value:{}, expireDuration:{}", key, value, expireDuration.toSeconds());
    }

    public String getData(String key) {
        return redisTemplate.opsForValue().get(key);
    }

    public boolean removeData(String key) {
        return redisTemplate.delete(key);
    }

    public Set<String> getDataKeys(String key) {
        return redisTemplate.keys(key);
    }

    public Long getExpire(String key) {
        return redisTemplate.getExpire(key);
    }

}