#include<stdio.h>

// int num;
// void setParam(int para)
// {
//     num = para;
// }

void run(unsigned char * temp, size_t length)
{
    for (size_t i = 0; i < length; i++)
    {
        (*(temp+i))++;
    }
    
}