/*
--- Simplified BSD License ---------------------------------------------------
Copyright (c) 2015, Robert Planas Jimenez
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the FreeBSD Project.
--------------------------------------------------------------------------------

This launcher is compiled using gcc, with Visual Studio 2015 on Windows.
Compilation commands:
	windres xyz.rc xyz.rc.o
	gcc -c launcher.c
	gcc -o launcher.exe launcher.o xyz.rc.o
*/

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

__mode_t mkdirmode = S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH;
extern int mkdir (const char *__path, __mode_t __mode);
extern int getcwd(char * text, size_t size);

#define ARG_SIZE 40
#define VAL_SIZE 100
#define COM_SIZE 600

#if defined(_WIN32) || defined(WIN32)
	#define _WIN32_IE 0x0400
	#include <Windows.h>
	#include <WinBase.h>
	#include <shlobj.h>
	#include <FileAPI.h>
#endif

char * launcher_name;
char * launcher_path;
char config_path[COM_SIZE];
char is_verbose = 0;
char no_msgbox = 0;

char default_config_file[] = \
"player: engine/blenderplayer\n"
"blend: data/game.blend\n\n"
"#video settings\n"
"resolution: 1280 768\n"
"fullscreen: true\n"
"stereomode: nostereo\n"
"anti-aliasing: 8\n\n"
"#game engine options\n"
"debug: false\n"
"fixedtime: false\n"
"nomipmap: false\n"
"show_framerate: false\n"
"show_properties: false\n"
"show_profile: false\n"
"blender_material: false\n"
"ignore_deprecation_warnings: true\n\n"
"#Custom command line\n"
"#exec: ./blenderplayer mygame.blend\n";

void sprintInfo(char * text);
void makeTempFile(char * filename);
void getTempDirectory(char * localdir);
void getLocalDirectory(char * localdir);

short is_between(int value, int from, int to){
	return value >= from && value <= to;
}

int file_exist(char *filename) {
	FILE * pFile;
	pFile = fopen(filename, "r");
	if (pFile == NULL) return 0;
	else {fclose(pFile); return 1;}
}

void substr(char *text, int i, int j) {
	if (j < 0) j = strlen(text) - i;

	char * tmp = strdup(text);
	while(i != 0) {
		tmp++; i--;
	}
	while(j != 0 && (*tmp) != '\0') {
		(*text) = (*tmp);
		text++; tmp++; j--;
	}
	(*text) = '\0';
}

//Returns True of no more text can be append, False and adds a EOL otherwise.
int append(char*s, size_t size, char c) {
	if(strlen(s) + 1 >= size) {
		return 1;
	}
	int len = strlen(s);
	s[len] = c;
	s[len+1] = '\0';
	return 0;
}

void remove_ext(char * text, char * ext) {
	char * tmp = strrchr(text, '.');
	if (tmp == NULL) return;
	if (strstr(tmp, ext) != NULL) {
		(*tmp) = '\0';
		return;
	}
}

int count(char *text, char ch) {
	int c = 0;
	while((*text) != '\0') {
		if (ch == *text) c++;
		text++;
	}
	return c;
}

int getParentDir(char *parent, char * text) {
	strncpy(parent, text, COM_SIZE);
	char * tmp = strrchr(parent, '/');
	if (tmp == NULL) return 0;
	(*(++tmp)) = '\0';
	return 1;
}

void getDirLevel(char *parent, char *path, int lvl) {
	strncpy(parent, path, COM_SIZE);
	int c = 0;
	char ch = '/';
	while((*parent) != '\0') {
		if (ch == *parent) c++;
		if (c == lvl) (*(++parent)) = '\0';
		parent++;
	}
}

void mkdirp(char * path) {
	char parent[COM_SIZE];
	getParentDir(parent, path);
	int c = count(parent, '/');
	int i = 2;
	for(; i<=c; i++) {
		getDirLevel(parent, path, i);
		if (mkdir(parent, mkdirmode) != 0) {
			if (errno != EEXIST && is_verbose) {
				printf("Error with mkdir: %s\n", parent);
			}
		}
	}

}

char * basename(char *text) {
	char * tmp = strrchr(text, '/');
	int diff = tmp-text;
	if (tmp == NULL) return text;
	if (diff == 0 || diff == strlen(text)-1) { (*tmp) = '\0'; return text; }
	return tmp+1;
}

int isAbsolutePath(char * exepath) {
	#if defined(_WIN32) || defined(WIN32)
	if (strlen(exepath) < 2) return 0;
	return (is_between(exepath[0], 'a', 'z') || is_between(exepath[0], 'A', 'Z')) && exepath[1] == ':' && (exepath[2] == '/' || exepath[2] == '\\');
	#else
	if (strlen(exepath) < 1) return 0;
	return (exepath[0] == '/');
	#endif
}

void replace_char(char *text, char a, char b) {
	while (*text != 0) {
		if (*text == a) (*text) = b;
		text++;
	}
}

void remove_char(char *text, char a) {
	char * pT = text;
	while (*pT != 0) {
		(*text) = (*pT);
		if (*pT != a) text++;
		pT++;
	}
	(*text) = (*pT);
}

#if defined(_WIN32) || defined(WIN32)
void msgbox(char *text) {
	if (no_msgbox) {
		printf("%s\n", text);
		return;
	}
	MessageBox(NULL, text, launcher_name, MB_OK);
}
#else
void msgbox(char *text) {
	if (no_msgbox) {
		printf("%s\n", text);
		return;
	}
	char * command;
	#if __APPLE__ && __MACH__
	sprintf(command, "osascript -e 'tell app \"System Events\" to display dialog \"%s\"'", text);
	#else
	sprintf(command, "xmessage -center \"%s\"", text);
	#endif
	system(command);
}
#endif

#if defined(_WIN32) || defined(WIN32)
void getTempDirectory(char * localdir) {
	GetTempPath(COM_SIZE, localdir);
	replace_char(localdir, '\\', '/');
}
#else
void getTempDirectory(char * localdir) {
	char* env = getenv("TMPDIR");
	if (env == NULL) env = "/var/tmp/";
	strcpy(localdir, env);
}
#endif

void loadGameProperty(FILE * pFile, char * data, char * name) {
	char temp[512];
	char * pT = temp;
	int found = 0;

	while (fgets(temp, 512, pFile) != NULL) {
		if ((pT = strstr(temp, name)) != NULL && pT == temp) {
			found = 1;
			break;
		}
	}
	if (found) {
		pT += strlen(name) + 2;
		strcpy(data, pT);
	}
	else (*data) = '\0';

}

void getLocalDirectory(char * localdir) {
	#if defined(_WIN32) || defined(WIN32)
	SHGetSpecialFolderPath(NULL, localdir, CSIDL_MYDOCUMENTS, TRUE);
	replace_char(localdir, '\\', '/');
	strcat(localdir, "/My Games/");
	#else
	char* env = getenv("HOME");
	strcpy(localdir, env);
	strncat(localdir, "/.local/share/", 14);
	#endif

	char _blend_name[COM_SIZE];
	char * blend_name = _blend_name;

	FILE * pFile = fopen(config_path, "r");
	if (pFile != NULL) {
		loadGameProperty(pFile, blend_name, "blend");
		replace_char(blend_name, '\\', '/');
		blend_name = basename(blend_name);
		remove_ext(blend_name, ".blend");
		fclose(pFile);
	}

	sprintf(localdir, "%s%s/", localdir, blend_name);
}

FILE * getConfigFile() {
	FILE * pFile;

	char * filename = "config.txt";
	getParentDir(config_path, launcher_path);
	strcat(config_path, filename);

	if (file_exist(config_path) == 0) {
		msgbox("No default config.txt file found!");
		return NULL;
	}
	pFile = fopen(config_path, "a");
	if (pFile == NULL)
	{
		//Get PATH
		char localdir[COM_SIZE];
		getLocalDirectory(localdir);

		strcat(localdir, filename);

		if (is_verbose) printf("Reading from local directory: %s\n", localdir);
		pFile = fopen(localdir, "r");
		if (pFile == NULL) {
			if (is_verbose) printf("Creating new configuration file.\n");
			char parent[COM_SIZE];
			getParentDir(parent, localdir);
			mkdirp(parent);
			pFile = fopen(localdir, "w");
			if (pFile == NULL) {
				msgbox("Error while loading configuration file. Permission denied.");
				return NULL;
			}
			FILE * oFile = fopen(config_path, "r");
			if (oFile == NULL) {
				fclose(pFile); return NULL;
			}

			char ch;
			while( ( ch = fgetc(oFile) ) != EOF ) fputc(ch, pFile);

			fclose(oFile); fclose(pFile);
			pFile = fopen(localdir, "r");
		}
		strncpy(config_path, localdir, COM_SIZE);

		//Now we update our info.txt file.
		char info[COM_SIZE];
		sprintInfo(info);

		getParentDir(localdir, config_path);
		strcat(localdir, "info.txt");

		FILE * iFile = fopen(localdir, "w");
		if (iFile != NULL) {
			fprintf(iFile, "%s", info);
			fclose(iFile);
		}
	}
	else {
		fclose(pFile);
		pFile = fopen(config_path, "r");
	}
	if (pFile == NULL) msgbox("Error while loading configuration file.");
	return pFile;
}

void generateConfigFileText() {
	char * code = default_config_file;

	FILE *f = fopen("config.txt", "w");
	if (f == NULL) {perror("Error trying to write the config file. \n"); printf("So, it will be print here: \n\n%s", code);}
	else {
		fprintf(f, "%s", code);
		fclose(f);
	}
}

void parseConfig(FILE *pFile, char * command, char * filename, char * exepath) {
	typedef enum {ARGUMENT, VALUE,	__IGNORE__} etype;
	char c, n = 0;
	etype mode = ARGUMENT;
	char arg[ARG_SIZE] = {0}, val[VAL_SIZE] = {0};

	fseek(pFile, 0, SEEK_END);
	rewind(pFile);
	do {
		c = fgetc (pFile);
		if (c == EOF) break;
		if (feof(pFile)) break;
		if (c=='\r') continue;
		if (c=='\n') {
			int val_p = n;
			mode=ARGUMENT; n=0;
			if (is_verbose && (strlen(arg) > 0)) printf("PARSING ARG: %s\n", arg);

			//Commands
			if (strcmp(arg, "player")==0) {
				strncat(exepath, val, val_p);
				if (is_verbose) printf("EXEPATH (player): %s\n", exepath);
			}
			if (strcmp(arg, "blend")==0) {
				strncat(filename, val, val_p);
				if (is_verbose) printf("FILENAME (blend): %s\n", filename);
			}

			if (strcmp(arg, "resolution")==0) {
				strncat(command, " -w ", 4);
				strncat(command, val, val_p);
				if (is_verbose) printf("COMMAND (resolution): %s\n", command);
			}
			if (strcmp(arg, "stereomode")==0) {
				strncat(command, " -s ", 4);
				strncat(command, val, val_p);
				if (is_verbose) printf("COMMAND (stereomode): %s\n", command);
			}
			if (strcmp(arg, "anti-aliasing")==0) {
				strncat(command, " -m ", 4);
				strncat(command, val, val_p);
				if (is_verbose) printf("COMMAND (anti-aliasing): %s\n", command);
			}

			//If you enable space offset then remember to enable this to.
			//if (strcmp(arg, "resolution")==0)	{strcat(command, " -w "); char * r = strtok (val,"x"); strcat(command, r);
			//					 r = strtok (NULL,"x"); strcat(command, " "); strcat(command, r); } //Warning!

			if (strcmp(arg, "fullscreen")==0 && strncmp(val, "true", 4)==0) {
				strncat(command, " -f", 3);
				if (is_verbose) printf("COMMAND (fullscreen): %s\n", command);
			}
			if (strcmp(arg, "debug")==0 && strncmp(val, "true", 4)==0) {
				strncat(command, " -d", 3);
				if (is_verbose) printf("COMMAND (debug): %s\n", command);
			}


			if (strcmp(arg, "fixedtime")==0 && strncmp(val, "true", 4)==0) strcat(command, " -g fixedtime = 1");
			if (strcmp(arg, "nomipmap")==0 && strncmp(val, "true", 4)==0) strcat(command, " -g nomipmap = 1");
			if (strcmp(arg, "show_framerate")==0 && strncmp(val, "true", 4)==0) strcat(command, " -g show_framerate = 1");
			if (strcmp(arg, "show_properties")==0 && strncmp(val, "true", 4)==0) strcat(command, " -g show_properties = 1");
			if (strcmp(arg, "show_profile")==0 && strncmp(val, "true", 4)==0) strcat(command, " -g show_profile = 1");
			if (strcmp(arg, "blender_material")==0 && strncmp(val, "true", 4)==0) strcat(command, " -g blender_material = 1");
			if (strcmp(arg, "ignore_deprecation_warnings")==0 && strncmp(val, "false", 4)==0) strcat(command, " -g ignore_deprecation_warnings = 0");

			if (strcmp(arg, "exec")==0 && strcmp(val, "")!=0) {
				memset(command, 0, COM_SIZE);
				strncpy(command, val, val_p);
				strncpy(filename, "", 0);
				break;
			}

			//Clean
			memset(arg, '\0', sizeof(arg));
			memset(val, '\0', sizeof(val));
			continue;
		}
		if (mode == __IGNORE__) continue;

		//Select modes
		if (c=='#') {mode = __IGNORE__; continue;}
		if (mode==ARGUMENT && c==':') {mode = VALUE; n=0; fseek(pFile, 1, SEEK_CUR); continue;}
		if (mode==ARGUMENT){
			if(append(arg, ARG_SIZE, c) == 1){
				printf("WARNING! option name have to have a length < %d(%d) chars : %s\n", ARG_SIZE, n, arg);
				mode = __IGNORE__;
				continue;
			}
		}
		if (mode==VALUE) {
			if(append(val, VAL_SIZE, c) == 1){
				printf("WARNING! option value have to have a length < %d(%d) chars : %s\n", VAL_SIZE, n, val);
				mode = __IGNORE__;
				continue;
			}
		}
		++n;
	}while(1);
	if (is_verbose) printf("COMMAND (ALL): %s\n", command);
}

char * findPlayerPath(char ** filepaths) {
	while (*filepaths != NULL) {
		char * path = (*filepaths);
		if(is_verbose) printf("Checking launcher: %s\n", path);
		if (file_exist(path)) return path;
		filepaths++;
	}
	return NULL;
}

#if defined(_WIN32) || defined(WIN32)
void getCommand(char * command, char * filename, char * exepath) {
	char abspath[VAL_SIZE];
	char quoted[VAL_SIZE];
	char buffer[COM_SIZE];
	if(isAbsolutePath(exepath)){
		sprintf(quoted, "\"%s\"", exepath);
	}else{
		GetModuleFileName(NULL, abspath, VAL_SIZE);
		char * n = strrchr(abspath, '\\');
		(*(++n)) = 0;
		replace_char(abspath, '\\', '/');
		sprintf(quoted, "\"%s%s\"", abspath, exepath);
	}
	strcpy(abspath, quoted);
	remove_char(abspath, '"');
	if (is_verbose) printf("ABSPATH: %s\n", abspath);
	if (file_exist(abspath) == 0) {
		TCHAR pf[MAX_PATH], pf86[MAX_PATH];
		SHGetSpecialFolderPath(NULL, pf, CSIDL_PROGRAM_FILES, FALSE);
		SHGetSpecialFolderPath(NULL, pf86, CSIDL_PROGRAM_FILESX86, FALSE);
		replace_char(pf, '\\', '/'); replace_char(pf86, '\\', '/');
		strcat(pf, "/Blender Foundation/Blender/blenderplayer.exe");
		strcat(pf86, "/Blender Foundation/Blender/blenderplayer.exe");
		char ** paths = (char *[]) {"engine/Blender/blenderplayer.exe", "C:/Program Files/Blender Foundation/Blender/blenderplayer.exe", pf, pf86, NULL};
		char * path = findPlayerPath(paths);

		if (path == NULL) {

			msgbox("The blender player is missing. You can download Blender from http://www.blender.org for free.");
			return;
		}
		sprintf(quoted, "%s", path);
	}

	sprintf(buffer, "\"\"%s\"%s \"%s\"\"", quoted, command, filename);
	strcpy(command, buffer);
}
#else
void getCommand(char * command, char * filename, char * exepath) {
	char tmp[COM_SIZE] = "./";
	if (file_exist(exepath) == 0) {
		char noexe[COM_SIZE];
		strncpy(noexe, exepath, COM_SIZE-3);
		substr(noexe, 0, strlen(noexe) - 4);
		char ** paths = (char *[]) {noexe, "engine/Blender/blenderplayer",
		"engine/blenderplayer.app/Contents/MacOS/blenderplayer",
		"/usr/bin/blenderplayer", "/opt/blender/blenderplayer", NULL};
		char * path = findPlayerPath(paths);
		if (path == NULL) {
			printf("No blenderplayer has been found!\n");
			msgbox("No blenderplayer found! \nPlease install Blender on your system or put a copy in the 'engine' directory. Last version is strongly recomended. \n\nwww.blender.org");
			return;
		}
		else strcpy(exepath, path);
		//strncpy(exepath, path, COM_SIZE-strlen(path));
	}
	else {
		strcat(tmp, exepath);
		strcpy(exepath, tmp);
	}
	sprintf(exepath, "%s%s \"%s\"", exepath, command, filename);
	strcpy(command, exepath);
}
#endif

void printHelp() {
	printf("This is the BGECore launcher, writted by Robert Planas. (BSD 2-Clause)\n\n");
	printf("--help or -h\tShow this dialog.\n");
	printf("-g\t\tGenerate a config file in the current directory. (Overwrite if exists)\n");
	printf("-v\t\tVerbose mode\n");
	printf("-w\t\tDo not create windows to display error messages.\n\n");
	printf("You can use -h on the blenderplayer to see the aviable commands.\n\n");
}

void sprintInfo(char * text) {
	char * filename = "config.txt";
	char tempdir[COM_SIZE] = ".";

	getTempDirectory(tempdir);

	sprintf(text, "#BGECore Launcher :::: Info\n"
		"ConfigFilepath: %s\n"
		"LauncherFilepath: %s\n"
		"TempDirectory: %s\n", config_path, launcher_path, tempdir);
}

void printInfo() {
	char localdir[COM_SIZE] = ".";
	sprintInfo(localdir);
	printf("%s", localdir);
}

void makeTempFile(char * filepath) {
	strcat(filepath, "BGECoreLauncherTempFile.txt");
	FILE *f = fopen(filepath, "w");
	if (f == NULL) perror("Error trying to write the temp file. \n");
	else {
		char text[COM_SIZE * 4];
		sprintInfo(text);
		fprintf(f, "%s", text);
		fclose(f);
	}
}

char _lfilepath[COM_SIZE];
int main(int argc, char * argv[])
{
	// --- handle arguments -------------------------------
	char* _fcom = argv[0];
	if (_fcom[0] == '.' && _fcom[1] == '/') _fcom+=2;
	strcpy(_lfilepath, _fcom);
	replace_char(_lfilepath, '\\', '/');
	launcher_path = _lfilepath;
	if (isAbsolutePath(launcher_path) == 0) {
		getcwd(launcher_path, COM_SIZE);
		replace_char(_lfilepath, '\\', '/');
		strcat(launcher_path, "/");
		strcat(launcher_path, _fcom);
	}

	launcher_name = _fcom;
	remove_ext(launcher_name, ".exe");
	replace_char(launcher_name, '\\', '/');
	launcher_name = basename(launcher_name);

	FILE *pFile = getConfigFile();

	if (argc>1) {
		if     (strcmp(argv[1],"-v")==0) is_verbose = 1;
		else if(strcmp(argv[1],"-w")==0) no_msgbox = 1;
		else {
			if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) printHelp();
			if (strcmp(argv[1], "-info") == 0) printInfo();
			if (strcmp(argv[1], "-g") == 0) generateConfigFileText();
			fclose(pFile);
			return 0;
		}
	}

	// --- normal use -------------------------------------------
	char command[COM_SIZE] = "";
	char filename[VAL_SIZE] = "";
	char exepath[COM_SIZE] = "";

	if (pFile == NULL) return 0;
	else {
		parseConfig(pFile, command, filename, exepath);
		fclose (pFile);
	}

	char * filepath;
	if (isAbsolutePath(filename) == 0) {
		char filepath_buff[COM_SIZE];
		getParentDir(filepath_buff, launcher_path);
		strncat(filepath_buff, filename, COM_SIZE);
		filepath = filepath_buff;
	}
	else filepath = filename;

	getCommand(command, filepath, exepath);
	if (is_verbose) printf("COMMAND: %s\n", command);
	system(command);
	return 0;

}
