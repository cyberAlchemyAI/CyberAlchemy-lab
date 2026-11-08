#define _GNU_SOURCE
#include <sys/stat.h>
#include <sys/types.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "native_members.h"

/* Static launcher: no host Python, shell, libcrypto or ELF interpreter is used. */
static void fail(const char *why) { fprintf(stderr,"selected-python: %s\n",why); exit(126); }
static void join(char *out,const char *a,const char *b) {
    if(snprintf(out,PATH_MAX,"%s/%s",a,b)>=PATH_MAX) fail("path exceeds bound");
}
static uint32_t rr(uint32_t v,int n) { return (v>>n)|(v<<(32-n)); }
static const uint32_t constants[64]={
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
typedef struct { uint32_t h[8]; uint64_t bytes; unsigned char block[64]; size_t used; } Sha;
static void compress(Sha *s) {
    uint32_t w[64],a,b,c,d,e,f,g,h;
    for(int i=0;i<16;i++) { unsigned char *p=s->block+4*i; w[i]=((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3]; }
    for(int i=16;i<64;i++) w[i]=w[i-16]+(rr(w[i-15],7)^rr(w[i-15],18)^(w[i-15]>>3))+w[i-7]+(rr(w[i-2],17)^rr(w[i-2],19)^(w[i-2]>>10));
    a=s->h[0];b=s->h[1];c=s->h[2];d=s->h[3];e=s->h[4];f=s->h[5];g=s->h[6];h=s->h[7];
    for(int i=0;i<64;i++) {
        uint32_t t1=h+(rr(e,6)^rr(e,11)^rr(e,25))+((e&f)^(~e&g))+constants[i]+w[i];
        uint32_t t2=(rr(a,2)^rr(a,13)^rr(a,22))+((a&b)^(a&c)^(b&c));
        h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;
    }
    uint32_t v[8]={a,b,c,d,e,f,g,h};for(int i=0;i<8;i++)s->h[i]+=v[i];
}
static void init(Sha *s) { *s=(Sha){{0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19},0,{0},0}; }
static void update(Sha *s,const unsigned char *p,size_t n) {
    s->bytes+=n;while(n) { size_t k=64-s->used;if(k>n)k=n;memcpy(s->block+s->used,p,k);s->used+=k;p+=k;n-=k;if(s->used==64){compress(s);s->used=0;} }
}
static void finish(Sha *s,char hex[65]) {
    uint64_t bits=s->bytes*8;s->block[s->used++]=0x80;
    if(s->used>56){memset(s->block+s->used,0,64-s->used);compress(s);s->used=0;}
    memset(s->block+s->used,0,56-s->used);for(int i=0;i<8;i++)s->block[63-i]=(unsigned char)(bits>>(8*i));compress(s);
    for(int i=0;i<8;i++)snprintf(hex+8*i,9,"%08x",s->h[i]);
}
static int stamp_equal(const struct stat *a,const struct stat *b) {
    return a->st_dev==b->st_dev && a->st_ino==b->st_ino && a->st_size==b->st_size && a->st_mode==b->st_mode
      && a->st_mtim.tv_sec==b->st_mtim.tv_sec && a->st_mtim.tv_nsec==b->st_mtim.tv_nsec
      && a->st_ctim.tv_sec==b->st_ctim.tv_sec && a->st_ctim.tv_nsec==b->st_ctim.tv_nsec;
}
static void ancestry(const char *path) {
    char p[PATH_MAX];if(strlen(path)>=sizeof(p)||path[0]!='/')fail("absolute path required");strcpy(p,path);
    for(char *c=p+1;;c++)if(*c=='/'||*c=='\0') { char saved=*c;*c='\0';struct stat st;
        if(lstat(p,&st)||!S_ISDIR(st.st_mode))fail("linked or missing directory ancestry");
        *c=saved;if(!saved)break;
    }
}
static void check_file(const char *path,const char *expected,uint64_t size,int mode) {
    struct stat before,after,attached;unsigned char block[65536];char actual[65];Sha hash;init(&hash);
    int fd=open(path,O_RDONLY|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC);if(fd<0)fail("selected member unavailable");
    if(fstat(fd,&before)||!S_ISREG(before.st_mode)||before.st_uid!=getuid()||before.st_nlink!=1
       ||(mode>=0 && (before.st_mode&0777)!=(mode_t)mode)||(uint64_t)before.st_size!=size)fail("selected member metadata differs");
    for(;;){ssize_t n=read(fd,block,sizeof(block));if(n<0){if(errno==EINTR)continue;fail("selected member read failed");}if(!n)break;update(&hash,block,(size_t)n);}
    if(fstat(fd,&after)||lstat(path,&attached)||!stamp_equal(&before,&after)||!stamp_equal(&before,&attached))fail("selected member changed during read");
    close(fd);finish(&hash,actual);if(strcmp(actual,expected))fail("selected member digest differs");
}
static int known(const char *name) {
    size_t low=0,high=NATIVE_MEMBER_COUNT;while(low<high){size_t mid=(low+high)/2;int cmp=strcmp(name,native_members[mid].name);if(!cmp)return 1;if(cmp<0)high=mid;else low=mid+1;}return 0;
}
static size_t inventory(const char *root,const char *relative) {
    char path[PATH_MAX];if(*relative)join(path,root,relative);else strcpy(path,root);
    DIR *dir=opendir(path);if(!dir)fail("selected native directory unavailable");size_t count=0;struct dirent *entry;
    for(;;) {
        errno=0;entry=readdir(dir);if(!entry){if(errno)fail("native inventory read failed");break;}
        if(!strcmp(entry->d_name,".")||!strcmp(entry->d_name,".."))continue;
        char name[PATH_MAX],full[PATH_MAX];if(*relative)join(name,relative,entry->d_name);else strcpy(name,entry->d_name);join(full,root,name);struct stat st;
        if(lstat(full,&st)||st.st_uid!=getuid())fail("native inventory ownership differs");
        if(S_ISDIR(st.st_mode)){if(st.st_mode&022)fail("native directory writable outside owner");count+=inventory(root,name);}
        else if(S_ISREG(st.st_mode)) {if(!known(name) && strcmp(name,"installation.json"))fail("undeclared native member");if(!strcmp(name,"installation.json") && ((st.st_mode&0777)!=0600||st.st_nlink!=1))fail("native receipt metadata differs");count++;}
        else fail("linked or special native inventory entry");
    }
    closedir(dir);return count;
}
int main(int argc,char **argv) {
    char self[PATH_MAX],root[PATH_MAX],parent[PATH_MAX],native[PATH_MAX],loader[PATH_MAX],python[PATH_MAX],abi[PATH_MAX],bootstrap[PATH_MAX];
    ssize_t n=readlink("/proc/self/exe",self,sizeof(self)-1);if(n<=0||(size_t)n>=sizeof(self)-1)fail("launcher executable origin unavailable");self[n]=0;
    const char suffix[]="/implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python";
    size_t length=strlen(self),tail=strlen(suffix);if(length<=tail||strcmp(self+length-tail,suffix))fail("launcher origin is not selected repository path");
    memcpy(root,self,length-tail);root[length-tail]=0;strcpy(parent,root);char *slash=strrchr(parent,'/');if(!slash||slash==parent)fail("repository parent unavailable");*slash=0;
    join(native,parent,".cal-runtime/native");ancestry(native);struct stat native_stat;
    if(lstat(native,&native_stat)||native_stat.st_uid!=getuid()||(native_stat.st_mode&0777)!=0700)fail("private installed native root required");
    if(inventory(native,"")!=NATIVE_MEMBER_COUNT+1)fail("native inventory is not exact1010 plus receipt");
    for(size_t i=0;i<NATIVE_MEMBER_COUNT;i++) { char path[PATH_MAX];join(path,native,native_members[i].name);check_file(path,native_members[i].sha256,native_members[i].size,native_members[i].mode); }
    join(bootstrap,root,"implementation/lab-runtime/local-host/t25-integrated-runtime-0004/child_bootstrap.py");
    char bootstrap_parent[PATH_MAX];strcpy(bootstrap_parent,bootstrap);*strrchr(bootstrap_parent,'/')=0;ancestry(bootstrap_parent);
    check_file(bootstrap,BOOTSTRAP_SHA256,BOOTSTRAP_SIZE,-1);
    join(loader,native,"lib/abi/ld-linux-x86-64.so.2");join(abi,native,"lib/abi");join(python,native,"bin/python");
    char **args=calloc((size_t)argc+24,sizeof(char*));if(!args)fail("argument allocation failed");int k=0,i=1,version=0;
    args[k++]=loader;args[k++]="--inhibit-cache";args[k++]="--library-path";args[k++]=abi;args[k++]=python;args[k++]="-I";args[k++]="-B";args[k++]="-S";
    while(i<argc && argv[i][0]=='-' && strcmp(argv[i],"-")) {
        char *v=argv[i];
        if(!strcmp(v,"--")||!strcmp(v,"-c")||!strcmp(v,"-m"))break;
        if(!strcmp(v,"-I")||!strcmp(v,"-B")||!strcmp(v,"-S")||!strcmp(v,"-E")||!strcmp(v,"-s")){i++;continue;}
        if(!strcmp(v,"-O")||!strcmp(v,"-OO")||!strcmp(v,"-u")||!strcmp(v,"-q")||!strcmp(v,"-Xutf8")||!strcmp(v,"-Xutf8=1")){args[k++]=v;i++;continue;}
        if(!strcmp(v,"-X") && i+1<argc && (!strcmp(argv[i+1],"utf8")||!strcmp(argv[i+1],"utf8=1"))){args[k++]=v;args[k++]=argv[i+1];i+=2;continue;}
        if((!strcmp(v,"-V")||!strcmp(v,"--version"))&&i==argc-1){args[k++]=v;version=1;i++;break;}
        fail("unsupported interpreter flag");
    }
    if(!version)args[k++]=bootstrap;
    for(;i<argc;i++)args[k++]=argv[i];
    args[k]=NULL;
    const char *clear[]={"LD_PRELOAD","LD_AUDIT","LD_LIBRARY_PATH","LD_DEBUG","LD_PROFILE","PYTHONPATH","PYTHONHOME","PYTHONUSERBASE","PYTHONSTARTUP","PYTHONINSPECT",NULL};
    for(int j=0;clear[j];j++)unsetenv(clear[j]);
    setenv("PYTHONDONTWRITEBYTECODE","1",1);
    execv(loader,args);fail("selected native execution failed");
}
