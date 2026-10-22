// ch01_staticlist.cpp —— 静态链表：数组模拟 next 指针、适用场景
//
//
// 【408 考点】
// 选择题：
// - 静态链表用数组存结点，next 域存的是"下一个结点的数组下标"（游标），不是地址
// - 又称"游标实现法"，适用于不支持指针的语言，或结点数目固定的场景
// - 王道约定：0 号单元作头结点，next == -1 表示结束（教材有的版本用 0 表示结束）
// - 判空：L.node[0].next == -1；求表长仍需 O(n) 遍历
// - 插入 / 删除只改 next，不移动元素 —— 这一点与链表相同
// - 但静态链表也要预先分配整块空间，容量固定 —— 这一点与顺序表相同
// - 逻辑上相邻的结点，物理位置（下标）不一定相邻 —— 与链表相同
// - 408 常考：给出一个静态链表的 (data, next) 数组，问插入 / 删除后 next 怎么变，
//   或者问"第 i 个元素存在哪个下标里"
// 算法设计题：
// - 静态链表的插入删除、按值删除、以及"如何自己管理空闲结点"
//
// 【结构定义】
// 数组的 0 号单元固定作头结点，data 域不用。
// node[i].next == -1 表示 i 是最后一个结点。
// 空闲结点也串成一条链（备用链表），freeHead 指向第一个空闲下标，-1 表示空间耗尽。
// 教材把备用链表头也塞进 0 号单元（space[0].cur），这里单列一个 freeHead，
// 两个链各管各的，读代码时不容易混。
//
// 【ASL / 复杂度】
// 按位查找：O(n)      按值查找：O(n)
// 按位插入 / 删除：O(n)（找第 i-1 个结点），改指针本身 O(1)
// malloc / free（MallocNode / FreeNode）：O(1)
// 空间：MAXSIZE 个结点，一次分配，不能扩容
//
// 【易错点】
// 1. next 存的是下标，不是地址，更不是"第几个元素"
// 2. 0 号单元是头结点，"下标 0"不等于"第 0 个元素"，位序从 1 开始
// 3. 结束标志全篇统一：王道用 -1，教材用 0。混用必错，本文件统一用 -1
// 4. 删除只是把结点从数据链摘下，还要挂回备用链，否则这块空间再也用不上
// 5. 插入前要判"空间耗尽"（MallocNode 返回 -1），等价于链表的 malloc 失败
// 6. 表长不是 MAXSIZE，也不是最后一个下标，必须从头结点开始数
// 7. 静态链表不能随机存取：想取第 i 个，只能从头结点顺着 next 走
//
// ============================================================================

#include<cstdio>
#include<cstdlib>

#define OK 1
#define ERROR 0

typedef int Status;
typedef int ElemType;

// 一、结构定义

#define MAXSIZE 10                 // 0 号单元作头结点，实际可存 MAXSIZE-1 个元素

typedef struct{
    ElemType data;
    int next;                      // 下一个结点的数组下标，-1 表示无后继
} SLinkNode;

typedef struct{
    SLinkNode node[MAXSIZE];
    int freeHead;                  // 备用链表头下标，-1 表示无空闲结点
} SLinkList;

// 二、基本操作

// 初始化：0 号单元作头结点；1..MAXSIZE-1 串成备用链表
Status InitList(SLinkList &L){
    L.node[0].next = -1;           // 空表
    for(int i=1; i<MAXSIZE-1; i++){
        L.node[i].next = i+1;
    }
    L.node[MAXSIZE-1].next = -1;
    L.freeHead = 1;
    return OK;
}

// 从备用链表取一个结点，返回其下标；返回 -1 表示空间耗尽
int MallocNode(SLinkList &L){
    int i = L.freeHead;
    if(i == -1) return -1;
    L.freeHead = L.node[i].next;
    L.node[i].next = -1;
    return i;
}

// 把下标为 i 的结点挂回备用链表
void FreeNode(SLinkList &L, int i){
    L.node[i].next = L.freeHead;
    L.freeHead = i;
}

// 判空
bool ListEmpty(SLinkList L){
    return L.node[0].next == -1;
}

// 求表长：从头结点顺着 next 数
int ListLength(SLinkList L){
    int len = 0;
    for(int p = L.node[0].next; p != -1; p = L.node[p].next){
        len++;
    }
    return len;
}

// 按位查找：用 e 返回第 i 个元素的值（位序从 1 开始）
Status GetElem(SLinkList L, int i, ElemType &e){
    if(i < 1) return ERROR;
    int p = L.node[0].next;
    int j = 1;
    while(p != -1 && j < i){
        p = L.node[p].next;
        j++;
    }
    if(p == -1) return ERROR;
    e = L.node[p].data;
    return OK;
}

// 按值查找：返回第一个值为 e 的元素的位序，找不到返回 0
int LocateElem(SLinkList L, ElemType e){
    int p = L.node[0].next;
    int j = 1;
    while(p != -1 && L.node[p].data != e){
        p = L.node[p].next;
        j++;
    }
    return (p == -1) ? 0 : j;
}

// 按位插入：在第 i 个位置插入 e（1 <= i <= length+1）
Status ListInsert(SLinkList &L, int i, ElemType e){
    if(i < 1) return ERROR;
    int pre = 0, j = 0;                 // pre 最终是第 i-1 个结点的下标，头结点为 0
    while(pre != -1 && j < i-1){
        pre = L.node[pre].next;
        j++;
    }
    if(pre == -1) return ERROR;         // i 超过 length+1
    int s = MallocNode(L);
    if(s == -1) return ERROR;           // 空间耗尽，相当于 malloc 失败
    L.node[s].data = e;
    L.node[s].next = L.node[pre].next;
    L.node[pre].next = s;
    return OK;
}

// 按位删除：删除第 i 个元素，用 e 返回其值
Status ListDelete(SLinkList &L, int i, ElemType &e){
    if(i < 1) return ERROR;
    int pre = 0, j = 0;
    while(pre != -1 && j < i-1){
        pre = L.node[pre].next;
        j++;
    }
    if(pre == -1 || L.node[pre].next == -1) return ERROR;
    int q = L.node[pre].next;
    e = L.node[q].data;
    L.node[pre].next = L.node[q].next;
    FreeNode(L, q);                     // 摘下后必须回收，否则这块空间永久丢失
    return OK;
}

// 打印：格式为 "下标:值"，用来看逻辑顺序与物理顺序的差别
void PrintList(SLinkList L){
    printf("Length: %d\n", ListLength(L));
    printf("  head[0].next = %d\n", L.node[0].next);
    printf("  (index:value)");
    for(int p = L.node[0].next; p != -1; p = L.node[p].next){
        printf("  %d:%d", p, L.node[p].data);
    }
    printf("\n");
}

// 打印备用链表，检查空闲结点有没有被正确回收
void PrintFree(SLinkList L){
    printf("  spare chain (freeHead = %d):", L.freeHead);
    for(int p = L.freeHead; p != -1; p = L.node[p].next){
        printf(" %d", p);
    }
    printf("\n");
}

//============================================================================
// 三、main() 自测

int main(){
    SLinkList L;
    InitList(L);
    printf("After init, ListEmpty = %d (expect 1)\n", (int)ListEmpty(L));
    PrintList(L);
    PrintFree(L);

    printf("\nInsert 10 20 30 40 at the tail:\n");
    for(int i=1; i<=4; i++){
        ListInsert(L, ListLength(L)+1, i*10);
    }
    PrintList(L);
    PrintFree(L);

    printf("\nDelete position 2 (20), the freed index goes back to the spare chain:\n");
    ElemType e;
    ListDelete(L, 2, e);
    printf("  deleted %d (expect 20)\n", e);
    PrintList(L);
    PrintFree(L);

    printf("\nInsert 50 at the tail, it reuses the freed index:\n");
    ListInsert(L, ListLength(L)+1, 50);
    PrintList(L);
    PrintFree(L);

    printf("\nGetElem(2) = ");
    if(GetElem(L, 2, e)) printf("%d (expect 30)\n", e);
    printf("LocateElem(40) = %d (expect 3)\n", LocateElem(L, 40));
    printf("LocateElem(99) = %d (expect 0)\n", LocateElem(L, 99));
    printf("GetElem(9) returns ERROR: %d\n", GetElem(L, 9, e) == ERROR);

    printf("\nFill the list until the space runs out:\n");
    int n = 0;
    while(ListInsert(L, ListLength(L)+1, 99)) n++;
    printf("  inserted %d more nodes, length = %d, capacity = %d\n",
           n, ListLength(L), MAXSIZE-1);
    printf("  one more insert returns ERROR: %d\n",
           ListInsert(L, ListLength(L)+1, 99) == ERROR);
    PrintList(L);
    PrintFree(L);

    printf("\nDelete from the head until empty:\n");
    while(ListDelete(L, 1, e)){
        printf("  deleted %d\n", e);
    }
    printf("ListEmpty = %d (expect 1)\n", (int)ListEmpty(L));
    PrintFree(L);

    return 0;
}
