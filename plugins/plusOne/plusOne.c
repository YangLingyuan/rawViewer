#include<stdio.h>

int num;
void setParam(int para)
{
    num = para;
}

int run(void)
{
    int temp = num + 1;
    printf("loading image from C plugin\nProcessed image is %d\n",temp);
    return temp;
}