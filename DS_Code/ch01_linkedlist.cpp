// ch01_linkedlist.cpp —— 单链表（带头结点）：头插 / 尾插 / 按位查找 / 插入 / 删除
//
//
// 【408 考点】
// 选择题：
// - 带头结点 vs 不带头结点：头结点不存数据，判空看 L->next == NULL
// - 头插法建立的链表与输入顺序相反，尾插法保持一致
// - 单链表按位查找 O(n)，按值查找 O(n)，插入删除本身只改指针 O(1)
// - "在 p 结点之前插入" 的 O(1) 偷懒做法：先插到 p 之后，再交换数据域
// - 删除结点 p 必须先保存 p->next 再 free(p)，否则断链
// 算法设计题：
// - 就地逆置、删重复、倒数第 k、判环、找交点、合并有序表
//   → 见 ch01_list_algorithms.cpp
//
// 【结构定义】
// 带头结点的单链表：头结点 data 域不用，next 指向第一个数据结点。
// 空表：L->next == NULL，此时 length == 0。
//
// 【ASL / 复杂度】
// 按位查找：O(n)，找第 i 个结点需走 i 步
// 按值查找：O(n)
// 插入：查第 i-1 个结点 O(n)，改指针 O(1)
// 删除：查第 i-1 个结点 O(n)，释放 O(1)
// 头插建表：O(n)，结果与输入顺序相反
// 尾插建表：O(n)，需额外维护尾指针 r
// 空间：每个结点一个指针域，整体 O(n)
//
// 【易错点】
// 1. 位序从 1 开始，头结点是第 0 个结点，不计入表长
// 2. 插入位置 i 合法范围：1 <= i <= length+1；删除：1 <= i <= length
// 3. 删除后必须 free(p)，并让前驱的 next 指向 p->next
// 4. 头插法把新结点插在头结点之后，所以输出顺序与输入相反
// 5. 尾插法建表时 r 始终指向最后一个结点，插入后要更新 r
// 6. 有了头结点，在第 1 个位置插入/删除不必特判表头，这是头结点的意义
//
// ============================================================================

#include<cstdio>
#include<cstdlib>

#define OK 1
#define ERROR 0

typedef int Status;
typedef int ElemType;

// 一、结构定义

typedef struct LNode{
    ElemType data;
    struct LNode *next;
} LNode, *LinkList;

// 二、基本操作

// 初始化：建立头结点，L 指向头结点
Status InitList(LinkList &L){
    L = (LNode*)malloc(sizeof(LNode));
    if(!L) return ERROR;
    L->next = NULL;
    return OK;
}

// 销毁：从头结点开始逐个释放
void DestroyList(LinkList &L){
    LNode *p = L;
    while(p){
        LNode *q = p->next;
        free(p);
        p = q;
    }
    L = NULL;
}

// 判空
bool ListEmpty(LinkList L){
    return L->next == NULL;
}

// 求表长（不含头结点）
int ListLength(LinkList L){
    int len = 0;
    LNode *p = L->next;
    while(p){
        len++;
        p = p->next;
    }
    return len;
}

// 按位查找：用 e 返回第 i 个元素的值（位序从 1 开始）
Status GetElem(LinkList L, int i, ElemType &e){
    if(i < 1) return ERROR;
    LNode *p = L;
    int j = 0;                 // j 为 p 所指结点的位序，头结点为 0
    while(p && j < i){
        p = p->next;
        j++;
    }
    if(!p) return ERROR;       // i 超出表长
    e = p->data;
    return OK;
}

// 按值查找：返回第一个值为 e 的结点的位序，找不到返回 0
int LocateElem(LinkList L, ElemType e){
    LNode *p = L->next;
    int j = 1;
    while(p && p->data != e){
        p = p->next;
        j++;
    }
    return p ? j : 0;
}

// 按位插入：在第 i 个位置插入元素 e
Status ListInsert(LinkList &L, int i, ElemType e){
    if(i < 1) return ERROR;
    LNode *p = L;              // p 最终指向第 i-1 个结点
    int j = 0;
    while(p && j < i-1){
        p = p->next;
        j++;
    }
    if(!p) return ERROR;       // i 超过 length+1
    LNode *s = (LNode*)malloc(sizeof(LNode));
    if(!s) return ERROR;
    s->data = e;
    s->next = p->next;
    p->next = s;
    return OK;
}

// 按位删除：删除第 i 个结点，用 e 返回其值
Status ListDelete(LinkList &L, int i, ElemType &e){
    if(i < 1) return ERROR;
    LNode *p = L;              // p 最终指向第 i-1 个结点
    int j = 0;
    while(p && j < i-1){
        p = p->next;
        j++;
    }
    if(!p || !p->next) return ERROR; // i 超过表长
    LNode *q = p->next;
    e = q->data;
    p->next = q->next;
    free(q);
    return OK;
}

// 头插法建表：n 个元素，结果与输入顺序相反
void CreateListHead(LinkList &L, ElemType a[], int n){
    L = (LNode*)malloc(sizeof(LNode));
    L->next = NULL;
    for(int i=0; i<n; i++){
        LNode *s = (LNode*)malloc(sizeof(LNode));
        s->data = a[i];
        s->next = L->next;     // 新结点始终插在头结点之后
        L->next = s;
    }
}

// 尾插法建表：n 个元素，结果与输入顺序一致
void CreateListTail(LinkList &L, ElemType a[], int n){
    L = (LNode*)malloc(sizeof(LNode));
    L->next = NULL;
    LNode *r = L;              // r 始终指向表尾结点
    for(int i=0; i<n; i++){
        LNode *s = (LNode*)malloc(sizeof(LNode));
        s->data = a[i];
        r->next = s;
        r = s;
    }
    r->next = NULL;
}

// 打印
void PrintList(LinkList L){
    printf("List length: %d\n", ListLength(L));
    for(LNode *p = L->next; p; p = p->next){
        printf("%d ", p->data);
    }
    printf("\n");
}

//============================================================================
// 三、main() 自测

int main(){
    int a[5] = {10, 20, 30, 40, 50};
    ElemType e;

    LinkList L;
    CreateListTail(L, a, 5);
    printf("Tail insert:\n");
    PrintList(L);

    GetElem(L, 3, e);
    printf("GetElem(3) = %d\n", e);
    printf("LocateElem(30) = %d\n", LocateElem(L, 30));
    printf("LocateElem(99) = %d\n", LocateElem(L, 99));

    ListInsert(L, 3, 25);
    printf("After insert 25 at 3:\n");
    PrintList(L);

    ListDelete(L, 5, e);
    printf("Deleted element: %d\n", e);
    PrintList(L);

    printf("ListEmpty = %d\n", (int)ListEmpty(L));
    DestroyList(L);
    printf("After destroy, L = %p\n", (void*)L);

    LinkList Lh;
    CreateListHead(Lh, a, 5);
    printf("Head insert:\n");
    PrintList(Lh);
    DestroyList(Lh);

    return 0;
}