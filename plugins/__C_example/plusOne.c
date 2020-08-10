#include<stdio.h>

int run(int num)
{
    int temp = num + 1;
    printf("loading image from C plugin\nProcessed image is %d\n",temp);
    return temp;
}