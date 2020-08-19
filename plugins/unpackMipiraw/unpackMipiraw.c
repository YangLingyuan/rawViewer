#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <sys/stat.h>
int num;
char _path[256];
u_int32_t _width;
u_int32_t _height;
u_int32_t _stride;
bool _loss;
void setParam(const char* path, u_int32_t width, u_int32_t height, u_int32_t bits, bool loss)
{
    strncpy(_path,path,256);
    _width  = width;
    _height = height;
    _stride = width*bits>>3;
    _loss   = loss;
    printf("_stride:%u \n",_stride);
}

int run(void)
{
    struct stat statbuf;
    stat(_path,&statbuf);
    printf("size of the file %ld \n", statbuf.st_size);
    FILE* fp = fopen(_path, "rb");
    if (!fp) {
        printf("Fail to open file <%s>\n", _path);
        return -1;
    }

    char fn[128];
    sprintf(fn, "unpack_%s", _path);
    FILE* fo = fopen(fn, "wb");
    if (!fo) {
        printf("Fail to open file <%s>\n", fn);
        fclose(fp);
        return -1;
    }

    u_int8_t* readLineBuff = (u_int8_t*)malloc(_stride*sizeof(u_int8_t));
    printf("readLineBuffer assigned:%p, buffer size:%lu \n",readLineBuff, sizeof(readLineBuff));
    fseek(fp, 0, SEEK_SET);

    for (size_t line = 0; line < _height; line++)
    {
        // printf("at line:%lu \n", line);
        size_t len = ftell(fp);
        // printf("pre-read fp:%lu \n", len);
        size_t result = fread(readLineBuff, sizeof(u_int8_t), (size_t)_stride, fp);
        // len = ftell(fp);
        // printf("post-read fp:%lu \n", len);
        if (_stride != result)
        {
            printf("read error, number of object read:%lu, current fp:%lu \n", result, len);
            free(readLineBuff);
            fclose(fo);
            fclose(fp);
            return -1;
        }
        for (size_t block = 0; block<_width>>2; block++)
        {
            u_int8_t *p = readLineBuff + 5 * block;
            u_int16_t pixel[4];
            pixel[0] = (u_int16_t)(p[0]) << 2;
            pixel[0] += (u_int16_t)p[4] & (u_int16_t)(0x03);
            pixel[1] = (u_int16_t)(p[1]) << 2;
            pixel[1] += (u_int16_t)p[4] & (u_int16_t)(0x0c);
            pixel[2] = (u_int16_t)(p[2]) << 2;
            pixel[2] += (u_int16_t)p[4] & (u_int16_t)(0x30);
            pixel[3] = (u_int16_t)(p[3]) << 2;
            pixel[3] += (u_int16_t)p[4] & (u_int16_t)(0xc0);
            fwrite(&pixel, sizeof(u_int16_t), 4, fo);
        }
    }

    free(readLineBuff);
    fclose(fo);
    fclose(fp);
    return 1;

}