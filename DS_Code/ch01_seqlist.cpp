// ch01_seqlist.cpp —— 顺序表：静态分配 + 动态分配
//
//
// 【408 考点】
// - 顺序表插入平均移动 n/2 次，删除平均移动 (n-1)/2 次
// - 位序从 1 开始，下标从 0 开始
// - 静态分配 vs 动态分配（容量固定 vs 可扩容）
// - 插入位置 i 的合法范围：1 <= i <= length+1
// - 删除位置 i 的合法范围：1 <= i <= length
// - 就地逆置、删除重复、合并有序表等（见 ch01_list_algorithms.cpp）
//
// 【结构定义】
// 静态分配：
// typedef struct{
//     ElemType data[MAXSIZE];
//     int length;
// } SqListStatic;
//
// 动态分配：malloc 一块连续空间，容量不足时 realloc 扩容
// typedef struct{
//     ElemType *data;
//     int length;
//     int MaxSize;
// } SqList;
//
// 【ASL / 复杂度】
// 插入：最好 O(1)（表尾），最坏 O(n)（表头），平均 O(n)
// 删除：最好 O(1)（表尾），最坏 O(n)（表头），平均 O(n)
// 按位查找：O(1)
// 按值查找：O(n)
//
// 【易错点】
// 1. 插入时先判断表满，再判断 i 是否合法
// 2. 插入时从后往前移，删除时从前往后移
//
// ============================================================================

#include<cstdio>
#include<cstdlib>

#define OK 1
#define ERROR 0
#define OVERFLOW -1

typedef int Statue;
typedef int ElemType;

// 一、静态分配顺序表

#define MAXSIZE 100
typedef struct{
    ElemType data[MAXSIZE];
    int length;
} SqListStatic;

Statue InitListStatic(SqListStatic &L){
    L.length =0;
    return OK;
}

bool ListEmptyStatic(SqListStatic L){
    return L.length == 0;
}

int ListLengthStatic(SqListStatic L){
    return L.length;
}

// 按位查找：返回第 i 个元素的值（位序从 1 开始）
Statue GetElemStatic(SqListStatic L, int i, ElemType &e){
    if(i<1 || i>L.length) return ERROR;
    e = L.data[i-1];
    return OK;
}

// 按值查找：返回第一个等于 e 的元素的位序，找不到返回 0
int LocateElemStatic(SqListStatic L, ElemType e){
    for(int i=0; i<L.length; i++){
        if(L.data[i] == e) return i+1; // 位序从 1 开始
    }
    return 0;
}

// 插入：在第 i 个位置插入元素 e(位序从 1 开始)
Statue ListInsertStatic(SqListStatic &L, int i, ElemType e){
    if(L.length == MAXSIZE) return ERROR; // 表满
    if(i<1 || i>L.length+1) return ERROR; // 插入位置不合法
    for(int j=L.length-1; j>=i-1; j--){ // 从后往前移
        L.data[j+1] = L.data[j];
    }
    L.data[i-1] = e;
    L.length++;
    return OK;
}

// 删除：删除第 i 个元素，用 e 返回其值
Statue ListDeleteStatic(SqListStatic &L, int i, ElemType &e){
    if(i<1 || i>L.length) return ERROR; // 删除位置不合法
    e = L.data[i-1];
    for(int j=i; j<L.length; j++){ // 从前往后移
        L.data[j-1] = L.data[j];
    }
    L.length--;
    return OK;
}

// 打印
void PrintListStatic(SqListStatic L){
    printf("List length: %d\n", L.length);
    for(int i=0; i<L.length; i++){
        printf("%d ", L.data[i]);
    }
    printf("\n");
}

//============================================================================
// 二、动态分配顺序表

#define INITSIZE 10
#define INCREMENT 5

typedef struct{
    ElemType *data;
    int length;
    int MaxSize;
} SqList;

Statue InitList(SqList &L){
    L.data = (ElemType*)malloc(INITSIZE * sizeof(ElemType));
    if(!L.data) exit(OVERFLOW);
    L.length = 0;
    L.MaxSize = INITSIZE;
    return OK;
}

void DestroyList(SqList &L){
    free(L.data);
    L.data = nullptr;
    L.length = 0;
    L.MaxSize = 0;
}

bool ListEmpty(SqList L){
    return L.length == 0;
}

int ListLength(SqList L){
    return L.length;
}

Statue IncreaseSize(SqList &L, int increment){
    ElemType *newData = (ElemType*)realloc(L.data, (L.MaxSize + increment) * sizeof(ElemType));
    if(!newData) exit(OVERFLOW);
    L.data = newData;
    L.MaxSize += increment;
    return OK;
}

Statue GetElem(SqList L, int i, ElemType &e){
    if(i<1 || i>L.length) return ERROR;
    e = L.data[i-1];
    return OK;
}

int LocateElem(SqList L, ElemType e){
    for(int i=0; i<L.length; i++){
        if(L.data[i] == e) return i+1;
    }
    return 0;
}

Statue ListInsert(SqList &L, int i, ElemType e){
    if(i<1 || i>L.length+1) return ERROR;
    if(L.length >= L.MaxSize) IncreaseSize(L, INCREMENT);
    for(int j=L.length-1; j>=i-1; j--){
        L.data[j+1] = L.data[j];
    }
    L.data[i-1] = e;
    L.length++;
    return OK;
}

Statue ListDelete(SqList &L, int i, ElemType &e){
    if(i<1 || i>L.length) return ERROR;
    e = L.data[i-1];
    for(int j=i; j<L.length; j++){
        L.data[j-1] = L.data[j];
    }
    L.length--;
    return OK;
}

void PrintList(SqList L){
    printf("List length: %d\n", L.length);
    for(int i=0; i<L.length; i++){
        printf("%d ", L.data[i]);
    }
    printf("\n");
}

//============================================================================
// 三、main() 自测

int main(){
    SqListStatic Ls;
    InitListStatic(Ls);
    for(int i=1; i<=5; i++){
        ListInsertStatic(Ls, i, i*10);
    }
    PrintListStatic(Ls);
    ElemType e;
    ListDeleteStatic(Ls, 3, e);
    printf("Deleted element: %d\n", e);
    PrintListStatic(Ls);

    SqList Ld;
    InitList(Ld);
    for(int i=1; i<=15; i++){
        ListInsert(Ld, i, i*10);
    }
    PrintList(Ld);
    ListDelete(Ld, 5, e);
    printf("Deleted element: %d\n", e);
    PrintList(Ld);
    DestroyList(Ld);

    return 0;
}