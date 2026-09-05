
#include <string.h>
#include <unistd.h>
#include <stdio.h>

// replace <fstream>
// https://www.cs.utah.edu/~germain/PPS/Topics/C_Language/file_IO.html




struct word_db_struct
{
    char character[20]  ;
    char pinyin[20];
    char eng[20];
    char inited;
};






void custom_strcat(char *dest, const char *source)
{
    while(*dest != '\0') /* finding the end of the string */
         dest++;

     while((*dest++ = *source++) != '\0') /* copy source */
        ;
}



void readHist( struct word_db_struct *word_db  ,char * file) {


  char * path= "/home/nybo/Projects/testcpp/data/";
  char fullpath[100] = ""; /* note that it must be large enough! */

  strcat(fullpath,path);
  strcat(fullpath,file);


  FILE *filee;
  filee = fopen(fullpath, "r");
  char line[256];
  int linenum=0;

  while (fgets(line, sizeof(line), filee)) {


    // vurder å ersatte
    char *character = strtok(line, "\t");
    char *pinyin = strtok(NULL, "\t");
    char *eng = strtok(NULL, "\t");

    // remove \n
    eng[strcspn ( eng, "\n" )] = '\0';

    strcpy(word_db[linenum].character, character);
    strcpy(word_db[linenum].pinyin, pinyin);
    strcpy(word_db[linenum].eng, eng);

    word_db[linenum].inited=1;
    linenum++;
  }


  strcpy(word_db[linenum].character, "\0");
  strcpy(word_db[linenum].pinyin, "\0");
  strcpy(word_db[linenum].eng, "\0");


  fclose(filee);


}













