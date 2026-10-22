// ch01_dlinkedlist.cpp —— 双链表：插入与删除的指针顺序（最容易写错的地方）
//
//
// 【408 考点】
// 选择题：
// - 双链表每个结点两个指针：prior 指向前驱，next 指向后继
// - 带头结点的双链表判空：L->next == NULL（同时 L->prior == NULL）
// - "能往回走"不等于"能随机存取"：双链表按位查找仍是 O(n)
// - 已知结点 p 时，前插、后插、删除 p 都是 O(1)，这是双链表相对单链表的唯一优势
// - 单链表要删 p 必须先找前驱 O(n)；双链表不用，p->prior 就是前驱
// - 带尾指针的双链表：尾插 O(1)，尾删也是 O(1)
//   （单链表带尾指针尾插 O(1)，但尾删仍要 O(n) 找前驱，这是常考的对比点）
// 算法设计题：
// - 双链表按值删除、就地逆置（逐个结点交换 prior 与 next）——思路同单链表，指针多一倍
//
// 【结构定义】
// typedef struct DNode{
//     ElemType data;
//     struct DNode *prior, *next;
// } DNode, *DLinkList;
//
// 头结点不存数据：L->prior == NULL，L->next 指向第一个数据结点。
// 尾结点 next == NULL；第一个数据结点的 prior 指向头结点。
//
// 【ASL / 复杂度】
// 按位查找：O(n)      按值查找：O(n)
// 已知 p 前插 / 后插 / 删除 p：O(1)
// 按位插入 / 删除：O(n)，时间全花在找第 i-1 或第 i 个结点上
// 头插 O(1)；带尾指针尾插 O(1)、尾删 O(1)
// 空间：每结点两个指针域，指针开销是单链表的两倍
//
// 【易错点】
// 1. p 是尾结点时 p->next == NULL，写 p->next->prior = s 直接崩，必须判空
// 2. 后插的四条语句顺序：先让新结点接上两边，最后才断开 p->next
//    s->next = p->next; if(p->next) p->next->prior = s; s->prior = p; p->next = s;
// 3. 前插同理：s->prior = p->prior; p->prior->next = s; s->next = p; p->prior = s;
// 4. 删除 p：p->prior->next = p->next; if(p->next) p->next->prior = p->prior; free(p);
//    忘了第二个判空，删尾结点时就会解引用 NULL
// 5. 头结点没有前驱，不能在它之前插入（p->prior 为 NULL），本文件里直接返回 ERROR
// 6. 非循环双链表的 L->prior 是 NULL，不是尾结点；
//    "L->prior 就是尾结点"只在循环双链表里成立（见 ch01_circularlist.cpp）
//
// ============================================================================

#include<cstdio>
#include<cstdlib>

#define OK 1
#define ERROR 0

typedef int Status;
typedef int ElemType;

// 一、结构定义

typedef struct DNode{
    ElemType data;
    struct DNode *prior, *next;
} DNode, *DLinkList;

// 二、基本操作

// 初始化：建立头结点，前后都为空
Status InitDList(DLinkList &L){
    L = (DNode*)malloc(sizeof(DNode));
    if(!L) return ERROR;
    L->prior = NULL;
    L->next = NULL;
    return OK;
}

// 销毁：顺着 next 逐个释放
void DestroyDList(DLinkList &L){
    DNode *p = L;
    while(p){
        DNode *q = p->next;
        free(p);
        p = q;
    }
    L = NULL;
}

// 判空
bool DListEmpty(DLinkList L){
    return L->next == NULL;
}

// 求表长（不含头结点）
int DListLength(DLinkList L){
    int len = 0;
    for(DNode *p = L->next; p; p = p->next){
        len++;
    }
    return len;
}

// 按位查找：用 e 返回第 i 个元素的值（位序从 1 开始）
Status GetElemD(DLinkList L, int i, ElemType &e){
    if(i < 1) return ERROR;
    DNode *p = L->next;
    int j = 1;
    while(p && j < i){
        p = p->next;
        j++;
    }
    if(!p) return ERROR;
    e = p->data;
    return OK;
}

// 按值查找：返回第一个值为 e 的结点的位序，找不到返回 0
int LocateElemD(DLinkList L, ElemType e){
    DNode *p = L->next;
    int j = 1;
    while(p && p->data != e){
        p = p->next;
        j++;
    }
    return p ? j : 0;
}

// 在 p 结点之后插入 e —— 注意 p 可能是尾结点
Status InsertNextDNode(DNode *p, ElemType e){
    if(!p) return ERROR;
    DNode *s = (DNode*)malloc(sizeof(DNode));
    if(!s) return ERROR;
    s->data = e;
    s->next = p->next;                 // ① 新结点接上后继
    if(p->next) p->next->prior = s;    // ② 后继回指新结点（p 是尾结点时跳过）
    s->prior = p;                      // ③ 新结点接上前驱
    p->next = s;                       // ④ 最后才断开 p 原来的 next
    return OK;
}

// 在 p 结点之前插入 e —— p 不能是头结点（头结点没有前驱）
Status InsertPriorDNode(DNode *p, ElemType e){
    if(!p || !p->prior) return ERROR;
    DNode *s = (DNode*)malloc(sizeof(DNode));
    if(!s) return ERROR;
    s->data = e;
    s->prior = p->prior;               // ① 新结点接上前驱
    p->prior->next = s;                // ② 前驱回指新结点
    s->next = p;                       // ③ 新结点接上后继
    p->prior = s;                      // ④ 最后才断开 p 原来的 prior
    return OK;
}

// 删除结点 p 本身（p 不能是头结点）
Status DeleteDNode(DLinkList L, DNode *p, ElemType &e){
    if(!p || p == L) return ERROR;
    e = p->data;
    p->prior->next = p->next;              // 前驱跨过 p
    if(p->next) p->next->prior = p->prior; // 后继跨过 p（p 是尾结点时跳过）
    free(p);
    return OK;
}

// 按位插入：在第 i 个位置插入 e（1 <= i <= length+1）
Status ListInsertD(DLinkList &L, int i, ElemType e){
    if(i < 1) return ERROR;
    DNode *p = L;                      // p 最终指向第 i-1 个结点
    int j = 0;
    while(p && j < i-1){
        p = p->next;
        j++;
    }
    if(!p) return ERROR;
    return InsertNextDNode(p, e);
}

// 按位删除：删除第 i 个结点，用 e 返回其值
Status ListDeleteD(DLinkList &L, int i, ElemType &e){
    if(i < 1) return ERROR;
    DNode *p = L;                      // p 最终指向第 i-1 个结点
    int j = 0;
    while(p && j < i-1){
        p = p->next;
        j++;
    }
    if(!p || !p->next) return ERROR;
    return DeleteDNode(L, p->next, e);
}

// 尾插法建表：返回尾结点指针，后面尾插 / 尾删都能 O(1)
DNode *CreateDListTail(DLinkList &L, ElemType a[], int n){
    L = (DNode*)malloc(sizeof(DNode));
    L->prior = NULL;
    L->next = NULL;
    DNode *r = L;
    for(int i=0; i<n; i++){
        DNode *s = (DNode*)malloc(sizeof(DNode));
        s->data = a[i];
        s->next = NULL;
        s->prior = r;
        r->next = s;
        r = s;
    }
    return r;
}

// 正序打印
void PrintDList(DLinkList L){
    printf("List length: %d\n", DListLength(L));
    printf("Forward : ");
    for(DNode *p = L->next; p; p = p->next){
        printf("%d ", p->data);
    }
    printf("\n");
}

// 逆序打印：先走到尾结点，再顺着 prior 回来
// 非循环双链表里 L->prior 是 NULL，不能当成尾结点用
void PrintDListReverse(DLinkList L){
    printf("Backward: ");
    if(!L->next){
        printf("(empty)\n");
        return;
    }
    DNode *p = L->next;
    while(p->next) p = p->next;
    for(; p != L; p = p->prior){
        printf("%d ", p->data);
    }
    printf("\n");
}

//============================================================================
// 三、main() 自测

int main(){
    int a[4] = {10, 20, 30, 40};
    ElemType e;

    DLinkList L;
    DNode *tail = CreateDListTail(L, a, 4);
    printf("Create by tail insert:\n");
    PrintDList(L);
    PrintDListReverse(L);
    printf("tail->data = %d (expect 40)\n", tail->data);

    printf("\nGetElemD(3) = ");
    if(GetElemD(L, 3, e)) printf("%d (expect 30)\n", e);
    printf("LocateElemD(40) = %d (expect 4)\n", LocateElemD(L, 40));
    printf("LocateElemD(99) = %d (expect 0)\n", LocateElemD(L, 99));
    printf("GetElemD(9) returns ERROR: %d\n", GetElemD(L, 9, e) == ERROR);

    printf("\nListInsertD(3, 25):\n");
    ListInsertD(L, 3, 25);
    PrintDList(L);

    // 已知结点 p 的 O(1) 前插 / 后插
    DNode *p = L->next->next->next;    // 第 3 个结点，值为 25
    InsertPriorDNode(p, 24);
    InsertNextDNode(p, 26);
    printf("\nAfter O(1) insert 24 before / 26 after node 3 (25):\n");
    PrintDList(L);
    PrintDListReverse(L);

    // 尾结点后插：p->next == NULL，走的是判空分支
    InsertNextDNode(tail, 45);
    printf("\nInsert 45 after the tail (p->next == NULL):\n");
    PrintDList(L);
    tail = tail->next;                 // 新的尾结点就是刚插在旧尾结点后面的那个
    printf("tail->data = %d (expect 45)\n", tail->data);

    printf("\nListDeleteD(1):\n");
    ListDeleteD(L, 1, e);
    printf("Deleted element: %d (expect 10)\n", e);
    PrintDList(L);

    // 尾删 O(1)：单链表做不到这一点
    printf("\nO(1) tail delete until empty:\n");
    while(tail != L){
        DNode *prev = tail->prior;
        DeleteDNode(L, tail, e);
        printf("  deleted tail %d\n", e);
        tail = prev;
    }
    printf("DListEmpty = %d (expect 1)\n", (int)DListEmpty(L));

    printf("ListDeleteD(1) on empty list returns ERROR: %d\n",
           ListDeleteD(L, 1, e) == ERROR);

    DestroyDList(L);
    printf("After destroy, L = %p\n", (void*)L);
    return 0;
}
