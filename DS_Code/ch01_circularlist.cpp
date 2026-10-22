// ch01_circularlist.cpp —— 循环单链表 / 循环双链表：判空条件与尾指针的应用
//
//
// 【408 考点】
// 选择题：
// - 循环单链表判空（带头结点）：L->next == L；不带头结点：head == NULL
// - 循环双链表判空：L->next == L && L->prior == L
// - 循环链表里没有 NULL 指针，遍历的终止条件是 p != L（或 p->next != L），
//   写成 p != NULL 必然死循环
// - 只有尾指针 r 的循环单链表：
//   表头插入 O(1)（r->next 就是头结点）
//   表尾插入 O(1)
//   表头删除 O(1)，表尾删除仍要 O(n)（单链表找前驱只能从头走）
//   → 这是"只有尾指针就能 O(1) 头尾操作"这一常见结论的边界
// - 循环双链表已知结点 p 时，前插/后插/删除都是 O(1)，四条指针顺序不能错
// 算法设计题：
// - 两个循环单链表合并、约瑟夫环、循环双链表就地调整
//
// 【结构定义】
// 循环单链表：尾结点 next 指回头结点，整个表首尾相接。
// 循环双链表：头结点 prior 指向尾结点，尾结点 next 指向头结点。
//
// 【ASL / 复杂度】
// 按位查找：O(n)
// 循环单链表：已知前驱插入/删除 O(1)；用尾指针 r 头插、尾插均 O(1)；删表尾 O(n)
// 循环双链表：已知结点 p，前插、后插、删除 p 均 O(1)
// 判空、求表长：O(1) / O(n)
//
// 【易错点】
// 1. 遍历终止：循环链表用 p != L，不能判 NULL
// 2. 头结点的 prior 也要维护：Init 时 L->prior = L，插入删除后仍然闭环
// 3. 只有尾指针 r 时 r->next 是头结点，r->next->next 才是第一个数据结点
// 4. 空表时 r 指回头结点；删掉唯一的结点后 r 要改回头结点
// 5. 双链表插入四条指针的正确顺序：先让新结点接上两边，再让邻居指向新结点
//    s->next = p->next; p->next->prior = s; s->prior = p; p->next = s;
//
// ============================================================================

#include<cstdio>
#include<cstdlib>

#define OK 1
#define ERROR 0

typedef int Status;
typedef int ElemType;

// 一、循环单链表（带头结点，常用尾指针 r）

typedef struct LNode{
    ElemType data;
    struct LNode *next;
} LNode, *CirLinkList;

// 初始化：头结点自己指向自己
Status InitCirList(CirLinkList &L){
    L = (LNode*)malloc(sizeof(LNode));
    if(!L) return ERROR;
    L->next = L;
    return OK;
}

// 判空：头结点的 next 指回自己
bool CirListEmpty(CirLinkList L){
    return L->next == L;
}

// 求表长：从第一个数据结点走到头结点
int CirListLength(CirLinkList L){
    int len = 0;
    for(LNode *p = L->next; p != L; p = p->next){
        len++;
    }
    return len;
}

// 尾插法建表，返回尾指针 r（空表时 r 就是头结点）
void CreateCirListTail(CirLinkList &r, ElemType a[], int n){
    LNode *head = (LNode*)malloc(sizeof(LNode));
    head->next = head;
    r = head;
    for(int i=0; i<n; i++){
        LNode *s = (LNode*)malloc(sizeof(LNode));
        s->data = a[i];
        s->next = head;        // 新尾结点始终指回头结点
        r->next = s;
        r = s;
    }
}

// 表头插入（插在第一个数据结点之前）：靠尾指针 r 做到 O(1)
Status CirInsertHead(CirLinkList &r, ElemType e){
    LNode *head = r->next;     // r->next 一定是头结点
    LNode *s = (LNode*)malloc(sizeof(LNode));
    if(!s) return ERROR;
    s->data = e;
    s->next = head->next;
    head->next = s;
    if(head == r) r = s;       // 原来是空表，新结点既是第一个也是最后一个
    return OK;
}

// 表尾插入：r 就是尾结点，直接接在后面
Status CirInsertTail(CirLinkList &r, ElemType e){
    LNode *s = (LNode*)malloc(sizeof(LNode));
    if(!s) return ERROR;
    s->data = e;
    s->next = r->next;         // 新尾结点指回头结点
    r->next = s;
    r = s;
    return OK;
}

// 删除第一个数据结点
Status CirDeleteHead(CirLinkList &r, ElemType &e){
    LNode *head = r->next;
    if(head->next == head) return ERROR; // 空表
    LNode *q = head->next;
    e = q->data;
    head->next = q->next;
    if(q == r) r = head;       // 删掉的是唯一结点，尾指针退回成头结点
    free(q);
    return OK;
}

// 打印
void PrintCirList(CirLinkList L){
    printf("List length: %d\n", CirListLength(L));
    for(LNode *p = L->next; p != L; p = p->next){
        printf("%d ", p->data);
    }
    printf("\n");
}

//============================================================================
// 二、循环双链表（带头结点）

typedef struct DNode{
    ElemType data;
    struct DNode *prior, *next;
} DNode, *DLinkList;

// 初始化：前后都指回自己
Status InitDList(DLinkList &L){
    L = (DNode*)malloc(sizeof(DNode));
    if(!L) return ERROR;
    L->next = L;
    L->prior = L;
    return OK;
}

// 判空
bool DListEmpty(DLinkList L){
    return L->next == L && L->prior == L;
}

// 在 p 结点之后插入 e
Status DInsertNext(DNode *p, ElemType e){
    DNode *s = (DNode*)malloc(sizeof(DNode));
    if(!s) return ERROR;
    s->data = e;
    s->next = p->next;
    p->next->prior = s;
    s->prior = p;
    p->next = s;
    return OK;
}

// 在 p 结点之前插入 e
Status DInsertPrior(DNode *p, ElemType e){
    DNode *s = (DNode*)malloc(sizeof(DNode));
    if(!s) return ERROR;
    s->data = e;
    s->prior = p->prior;
    p->prior->next = s;
    s->next = p;
    p->prior = s;
    return OK;
}

// 删除 p 结点本身（p 不能是头结点）
Status DDeleteNode(DLinkList L, DNode *p, ElemType &e){
    if(p == L) return ERROR;
    e = p->data;
    p->prior->next = p->next;
    p->next->prior = p->prior;
    free(p);
    return OK;
}

// 按位查找：返回第 i 个数据结点的指针，找不到返回 NULL
DNode *DGetElem(DLinkList L, int i){
    if(i < 1) return NULL;
    DNode *p = L->next;
    int j = 1;
    while(p != L && j < i){
        p = p->next;
        j++;
    }
    return (p == L) ? NULL : p;
}

// 正序 / 逆序打印
void PrintDList(DLinkList L){
    printf("Forward : ");
    for(DNode *p = L->next; p != L; p = p->next){
        printf("%d ", p->data);
    }
    printf("\nBackward: ");
    for(DNode *p = L->prior; p != L; p = p->prior){
        printf("%d ", p->data);
    }
    printf("\n");
}

//============================================================================
// 三、main() 自测

int main(){
    int a[4] = {10, 20, 30, 40};
    ElemType e;

    // 循环单链表：只保存尾指针 r
    CirLinkList r;
    CreateCirListTail(r, a, 4);
    printf("Circular single list:\n");
    PrintCirList(r->next);            // r->next 是头结点
    printf("r->data = %d (tail)\n", r->data);

    CirInsertHead(r, 5);              // O(1) 头插
    CirInsertTail(r, 50);             // O(1) 尾插
    printf("After head insert 5 and tail insert 50:\n");
    PrintCirList(r->next);
    printf("r->data = %d (tail)\n", r->data);

    CirDeleteHead(r, e);
    printf("Deleted first element: %d\n", e);
    PrintCirList(r->next);

    // 空表判定：把元素逐个删光
    while(CirDeleteHead(r, e)){}
    printf("CirListEmpty = %d, r == head: %d\n",
           (int)CirListEmpty(r->next), (int)(r == r->next));

    // 循环双链表
    DLinkList L;
    InitDList(L);
    printf("\nCircular double list, DListEmpty = %d\n", (int)DListEmpty(L));
    for(int i=0; i<4; i++){
        DInsertNext(L, a[i]);         // 依次后插到表头之后
    }
    PrintDList(L);

    DNode *p = DGetElem(L, 2);        // 第 2 个数据结点，值为 30
    DInsertPrior(p, 25);              // O(1) 前插
    DInsertNext(p, 35);               // O(1) 后插
    printf("After insert 25 before and 35 after node 2:\n");
    PrintDList(L);

    p = DGetElem(L, 1);
    DDeleteNode(L, p, e);             // 删第一个数据结点 20
    printf("Deleted element: %d\n", e);
    PrintDList(L);

    return 0;
}