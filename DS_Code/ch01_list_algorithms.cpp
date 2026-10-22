// ch01_list_algorithms.cpp —— 线性表算法设计题合集
//
//
// 【408 考点】
// 顺序表：
// - 就地逆置：首尾双指针交换，O(n) 时间 O(1) 空间
// - 删除所有值为 x 的元素：双指针覆盖，O(n) 时间 O(1) 空间，且保持相对顺序
// - 循环左移 p 位（2010 真题）：三次逆置，O(n) 时间 O(1) 空间
// - 两个等长升序序列的中位数（2011 真题）：二分，O(log n) 时间 O(1) 空间
// 单链表：
// - 就地逆置：头插法重建，O(n) 时间 O(1) 空间
// - 递归删除值为 x 的结点：递归深度 O(n)
// - 无序表删重复：双重循环 O(n^2)/O(1)；有序表删重复：一趟 O(n)/O(1)
// - 倒数第 k 个结点（2009 真题）：双指针，一趟扫描
// - 判环 + 找环入口：快慢指针
// - 两个链表的第一个公共结点（2012 真题）：长度差对齐
// - 合并两个有序表：归并，复用原结点，O(n+m)
// - 按位序奇偶拆分 / 按值拆分：尾插保持相对顺序
// - 删除有序表中 (minK, maxK) 之间的元素
// - 重排链表 a1,an,a2,an-1,...（2019 真题）：找中点 + 逆置后半 + 合并
//
// 【答题格式】408 算法设计题给分点：思路说明 → 代码 → 时间复杂度 / 空间复杂度。
// 本文件每个函数上方的注释就是按这个顺序写的，抄到答题纸上时把注释翻成文字即可。
//
// 【易错点】
// 1. 链表题先想清楚"带不带头结点"，本文件全部带头结点
// 2. 改指针前先保存后继，否则断链后再也找不到后面的结点
// 3. 释放结点后不能再访问它的 next，先存到临时变量
// 4. 双指针的边界：k 比表长还大要返回 NULL；环入口的推导要能写出来
// 5. 顺序表的覆盖类算法，循环结束后别忘了把 length 改成 k
// 6. 合并 / 拆分类算法要"只改指针、不复制数据"，否则空间复杂度变成 O(n)
//
// ============================================================================

#include<cstdio>
#include<cstdlib>

#define OK 1
#define ERROR 0

typedef int Status;
typedef int ElemType;

//============================================================================
// 一、顺序表上的算法设计题
//============================================================================

#define MAXSIZE 50

typedef struct{
    ElemType data[MAXSIZE];
    int length;
} SqList;

void InitSq(SqList &L, const ElemType a[], int n){
    L.length = n;
    for(int i=0; i<n; i++) L.data[i] = a[i];
}

void PrintSq(const char *tag, SqList L){
    printf("%s: ", tag);
    if(L.length == 0) printf("(empty)");
    for(int i=0; i<L.length; i++) printf("%d ", L.data[i]);
    printf("\n");
}

// 下标区间 [left, right] 就地逆置，供后面三个算法复用
static void ReverseRange(ElemType a[], int left, int right){
    while(left < right){
        ElemType t = a[left];
        a[left] = a[right];
        a[right] = t;
        left++;
        right--;
    }
}

// 【1】就地逆置顺序表
// 思路：第 i 个与第 n-1-i 个交换，走到中间即止
// 复杂度：时间 O(n)，空间 O(1)
void ReverseSq(SqList &L){
    ReverseRange(L.data, 0, L.length-1);
}

// 【2】删除顺序表中所有值为 x 的元素（2010 年前后的常考题）
// 思路：k 记录"保留下来的元素个数"，一遍扫描，等于 x 就跳过，不等就写到 data[k]
// 复杂度：时间 O(n)，空间 O(1)；相对顺序不变
// 返回：实际删除的个数
int DelXSeq(SqList &L, ElemType x){
    int k = 0;
    for(int i=0; i<L.length; i++){
        if(L.data[i] != x) L.data[k++] = L.data[i];
    }
    int removed = L.length - k;
    L.length = k;
    return removed;
}

// 【3】循环左移 p 位（2010 真题）
// 思路：把表看成 ab 两段（a 长 p，b 长 n-p），目标是 ba。
//       先逆置 a 得 a^-1 b，再逆置 b 得 a^-1 b^-1，最后整体逆置得 ba
// 复杂度：时间 O(n)，空间 O(1)
void LeftRotate(SqList &L, int p){
    if(L.length == 0) return;
    p %= L.length;
    if(p <= 0) return;
    ReverseRange(L.data, 0, p-1);
    ReverseRange(L.data, p, L.length-1);
    ReverseRange(L.data, 0, L.length-1);
}

// 【4】两个等长升序序列的中位数（2011 真题）
// 思路：分别取两段的中位数 A[m1]、B[m2]，
//       A[m1] == B[m2] 直接返回；
//       A[m1] < B[m2]：答案在 A 的右半段与 B 的左半段里，两段等长地缩；
//       A[m1] > B[m2]：对称处理。
//       缩到各剩一个元素时，取较小者即为下中位数。
// 复杂度：时间 O(log n)，空间 O(1)
int MedianSorted(int A[], int B[], int n){
    int s1 = 0, d1 = n-1;
    int s2 = 0, d2 = n-1;
    while(s1 != d1 || s2 != d2){
        int m1 = (s1 + d1) / 2;
        int m2 = (s2 + d2) / 2;
        if(A[m1] == B[m2]) return A[m1];
        if(A[m1] < B[m2]){
            if((s1 + d1) % 2 == 0){    // 本段元素个数为奇数，保留中点
                s1 = m1;
                d2 = m2;
            } else {                   // 偶数个，舍弃中点的左半边
                s1 = m1 + 1;
                d2 = m2;
            }
        } else {
            if((s1 + d1) % 2 == 0){
                d1 = m1;
                s2 = m2;
            } else {
                d1 = m1;
                s2 = m2 + 1;
            }
        }
    }
    return A[s1] < B[s2] ? A[s1] : B[s2];
}

// 对拍用的暴力版：合并后排序，取第 n 个（下标 n-1）
static void InsertSortInt(int a[], int n){
    for(int i=1; i<n; i++){
        int t = a[i], j = i-1;
        while(j >= 0 && a[j] > t){
            a[j+1] = a[j];
            j--;
        }
        a[j+1] = t;
    }
}

static int MedianBrute(int A[], int B[], int n){
    int tmp[64];
    for(int i=0; i<n; i++){
        tmp[i] = A[i];
        tmp[n+i] = B[i];
    }
    InsertSortInt(tmp, 2*n);
    return tmp[n-1];
}

//============================================================================
// 二、单链表上的算法设计题（全部带头结点）
//============================================================================

typedef struct LNode{
    ElemType data;
    struct LNode *next;
} LNode, *LinkList;

int ListLength(LinkList L){
    int len = 0;
    for(LNode *p = L->next; p; p = p->next) len++;
    return len;
}

// 尾插建表
LinkList BuildList(const ElemType a[], int n){
    LinkList L = (LNode*)malloc(sizeof(LNode));
    L->next = NULL;
    LNode *r = L;
    for(int i=0; i<n; i++){
        LNode *s = (LNode*)malloc(sizeof(LNode));
        s->data = a[i];
        s->next = NULL;
        r->next = s;
        r = s;
    }
    return L;
}

void DestroyList(LinkList &L){
    LNode *p = L;
    while(p){
        LNode *q = p->next;
        free(p);
        p = q;
    }
    L = NULL;
}

void PrintL(const char *tag, LinkList L){
    printf("%s: ", tag);
    if(!L->next) printf("(empty)");
    for(LNode *p = L->next; p; p = p->next) printf("%d ", p->data);
    printf("\n");
}

// 返回第 i 个数据结点（位序从 1 开始），找不到返回 NULL
LNode *NodeAt(LinkList L, int i){
    LNode *p = L->next;
    int j = 1;
    while(p && j < i){
        p = p->next;
        j++;
    }
    return p;
}

// 【5】单链表就地逆置
// 思路：把原表结点逐个摘下，头插到 L 之后；摘之前先存后继
// 复杂度：时间 O(n)，空间 O(1)
void ReverseList(LinkList L){
    LNode *p = L->next;
    L->next = NULL;
    while(p){
        LNode *q = p->next;    // 先存后继，否则断链
        p->next = L->next;     // 头插
        L->next = p;
        p = q;
    }
}

// 【6】递归删除所有值为 x 的结点（头结点不参与判断时传 L->next）
// 思路：若当前结点就是 x，释放它，并让"上一层存下来的指针"直接指向它的后继；
//       否则递归处理 next。L 是引用参数，删掉头一个结点时自动改写调用方的指针。
// 复杂度：时间 O(n)，空间 O(n)（递归栈）
void DelXRecur(LinkList &L, ElemType x){
    if(!L) return;
    if(L->data == x){
        LNode *q = L;
        L = L->next;
        free(q);
        DelXRecur(L, x);
    } else {
        DelXRecur(L->next, x);
    }
}

// 【6'】迭代版：pre 始终是 p 的前驱
// 复杂度：时间 O(n)，空间 O(1)
int DelXIter(LinkList L, ElemType x){
    int cnt = 0;
    LNode *pre = L, *p = L->next;
    while(p){
        if(p->data == x){
            pre->next = p->next;
            free(p);
            p = pre->next;
            cnt++;
        } else {
            pre = p;
            p = p->next;
        }
    }
    return cnt;
}

// 【7】无序表删除重复结点（只保留第一次出现的值）
// 思路：对每个结点 p，用它后面的 q 逐个比对，相同就删 q
// 复杂度：时间 O(n^2)，空间 O(1)
// 若允许 O(n) 辅助空间，可开一个计数数组 / 哈希表做到 O(n)，考纲更偏爱前者
int DelDupUnsorted(LinkList L){
    int cnt = 0;
    for(LNode *p = L->next; p; p = p->next){
        LNode *pre = p;
        LNode *q = p->next;
        while(q){
            if(q->data == p->data){
                pre->next = q->next;
                free(q);
                q = pre->next;
                cnt++;
            } else {
                pre = q;
                q = q->next;
            }
        }
    }
    return cnt;
}

// 【8】有序表删除重复结点
// 思路：重复的元素一定相邻，一次扫描即可
// 复杂度：时间 O(n)，空间 O(1)
int DelDupSorted(LinkList L){
    int cnt = 0;
    LNode *p = L->next;
    while(p && p->next){
        if(p->data == p->next->data){
            LNode *q = p->next;
            p->next = q->next;
            free(q);
            cnt++;
        } else {
            p = p->next;
        }
    }
    return cnt;
}

// 【9】找倒数第 k 个结点（2009 真题）
// 思路：p 先走 k 步，然后 p、q 同步走；p 到表尾时 q 正好是倒数第 k 个
// 复杂度：时间 O(n)（一趟扫描），空间 O(1)
LNode *KthFromEnd(LinkList L, int k){
    if(k < 1) return NULL;
    LNode *p = L->next, *q = L->next;
    for(int i=0; i<k; i++){
        if(!p) return NULL;    // k 比表长还大
        p = p->next;
    }
    while(p){
        p = p->next;
        q = q->next;
    }
    return q;
}

// 【10】判环：快慢指针，相遇即有环，返回相遇点；无环返回 NULL
// 复杂度：时间 O(n)，空间 O(1)
LNode *HasCycle(LinkList L){
    LNode *slow = L->next, *fast = L->next;
    while(fast && fast->next){
        slow = slow->next;
        fast = fast->next->next;
        if(slow == fast) return slow;
    }
    return NULL;
}

// 【10'】找环入口：相遇后一个指针回到起点，两个指针同速前进，再次相遇即入口
// 推导：设头到入口距离 a，入口到相遇点距离 b，环长 r，则 a = r - b（mod r）
// 复杂度：时间 O(n)，空间 O(1)
LNode *CycleEntry(LinkList L){
    LNode *meet = HasCycle(L);
    if(!meet) return NULL;
    LNode *p = L->next;
    while(p != meet){
        p = p->next;
        meet = meet->next;
    }
    return p;
}

// 【11】两个链表的第一个公共结点（2012 真题）
// 思路：先求长度差，让长的先走差值步，再同步走，第一个相同指针就是交点
// 复杂度：时间 O(m+n)，空间 O(1)；不能用"值相等"判断，必须比结点地址
LNode *FirstCommonNode(LinkList A, LinkList B){
    int la = ListLength(A), lb = ListLength(B);
    LNode *pa = A->next, *pb = B->next;
    while(la > lb){ pa = pa->next; la--; }
    while(lb > la){ pb = pb->next; lb--; }
    while(pa && pa != pb){
        pa = pa->next;
        pb = pb->next;
    }
    return pa;
}

// 【12】合并两个递增有序表（结果仍递增，复用原结点）
// 思路：归并，r 指向结果表尾；等号取 A 的结点可保证稳定
// 复杂度：时间 O(m+n)，空间 O(1)；B 的头结点被释放
LinkList MergeSorted(LinkList &A, LinkList &B){
    LNode *pa = A->next, *pb = B->next;
    LNode *r = A;
    A->next = NULL;
    while(pa && pb){
        if(pa->data <= pb->data){
            r->next = pa;
            r = pa;
            pa = pa->next;
        } else {
            r->next = pb;
            r = pb;
            pb = pb->next;
        }
    }
    r->next = pa ? pa : pb;
    free(B);
    B = NULL;
    return A;
}

// 【13】按位序奇偶拆成两个表，各自保持原相对顺序
// 思路：尾插，避免头插把顺序弄反
// 复杂度：时间 O(n)，空间 O(1)（只新建两个头结点）
void SplitOddEven(LinkList L, LinkList &A, LinkList &B){
    A = (LNode*)malloc(sizeof(LNode));
    B = (LNode*)malloc(sizeof(LNode));
    A->next = NULL;
    B->next = NULL;
    LNode *ra = A, *rb = B;
    int i = 1;
    for(LNode *p = L->next; p; p = p->next, i++){
        if(i % 2 == 1){
            ra->next = p;
            ra = p;
        } else {
            rb->next = p;
            rb = p;
        }
    }
    ra->next = NULL;
    rb->next = NULL;
    L->next = NULL;
}

// 【14】按值拆成两个表：小于 x 的一边，其余另一边，各自保持原相对顺序
// 复杂度：时间 O(n)，空间 O(1)
void SplitByValue(LinkList L, ElemType x, LinkList &A, LinkList &B){
    A = (LNode*)malloc(sizeof(LNode));
    B = (LNode*)malloc(sizeof(LNode));
    A->next = NULL;
    B->next = NULL;
    LNode *ra = A, *rb = B;
    for(LNode *p = L->next; p; p = p->next){
        if(p->data < x){
            ra->next = p;
            ra = p;
        } else {
            rb->next = p;
            rb = p;
        }
    }
    ra->next = NULL;
    rb->next = NULL;
    L->next = NULL;
}

// 【15】删除递增有序表中值在 (minK, maxK) 内的所有元素
// 思路：先走到第一个 > minK 的结点，再一路删到第一个 >= maxK 的结点
// 复杂度：时间 O(n)，空间 O(1)
int DeleteRange(LinkList L, ElemType minK, ElemType maxK){
    int cnt = 0;
    LNode *pre = L, *p = L->next;
    while(p && p->data <= minK){
        pre = p;
        p = p->next;
    }
    while(p && p->data < maxK){
        LNode *q = p->next;
        free(p);
        p = q;
        cnt++;
    }
    pre->next = p;
    return cnt;
}

// 【16】重排链表：a1, an, a2, an-1, ...（2019 真题）
// 思路：快慢指针找中点 → 就地逆置后半段 → 两段交替合并
// 复杂度：时间 O(n)，空间 O(1)
void ReorderList(LinkList L){
    if(!L->next || !L->next->next) return;

    LNode *slow = L->next, *fast = L->next;
    while(fast->next && fast->next->next){
        slow = slow->next;
        fast = fast->next->next;
    }

    LNode *second = slow->next;    // 后半段的第一个结点
    slow->next = NULL;             // 前半段就地截断

    LNode *rev = NULL;             // 逆置后半段
    while(second){
        LNode *t = second->next;
        second->next = rev;
        rev = second;
        second = t;
    }

    LNode *p = L->next, *q = rev, *r = L;   // 交替合并
    while(p && q){
        r->next = p;
        r = p;
        p = p->next;
        r->next = q;
        r = q;
        q = q->next;
    }
    r->next = p ? p : q;
}

//============================================================================
// 三、main() 自测
//============================================================================

int main(){
    // ── 顺序表 ────────────────────────────────────────────────
    printf("===== Sequential list =====\n");
    ElemType a1[] = {1, 2, 3, 4, 5, 6};
    SqList L;
    InitSq(L, a1, 6);
    PrintSq("Original             ", L);

    LeftRotate(L, 3);
    PrintSq("LeftRotate 3         ", L);   // expect 4 5 6 1 2 3
    LeftRotate(L, 6);
    PrintSq("LeftRotate 6 (no-op) ", L);   // expect unchanged

    ReverseSq(L);
    PrintSq("ReverseSq            ", L);   // expect 3 2 1 6 5 4

    ElemType a2[] = {1, 2, 2, 3, 2, 4};
    InitSq(L, a2, 6);
    int removed = DelXSeq(L, 2);
    PrintSq("DelXSeq(2)           ", L);   // expect 1 3 4
    printf("  removed %d (expect 3)\n", removed);

    int A[] = {11, 13, 15, 17, 19};
    int B[] = {2, 4, 6, 8, 20};
    printf("\nMedianSorted([11 13 15 17 19], [2 4 6 8 20]) = %d (expect 11)\n",
           MedianSorted(A, B, 5));

    // 对拍：随机生成等长升序序列，和暴力解逐例比对
    srand(20261022);
    int bad = 0;
    for(int t=0; t<500; t++){
        int n = 1 + rand() % 12;
        int X[20], Y[20];
        for(int i=0; i<n; i++){
            X[i] = rand() % 100;
            Y[i] = rand() % 100;
        }
        InsertSortInt(X, n);
        InsertSortInt(Y, n);
        if(MedianSorted(X, Y, n) != MedianBrute(X, Y, n)) bad++;
    }
    printf("Median cross-check: 500 random cases, mismatches = %d (expect 0)\n", bad);

    // ── 单链表 ────────────────────────────────────────────────
    printf("\n===== Linked list =====\n");
    ElemType l1[] = {1, 2, 3, 4, 5};
    LinkList L1 = BuildList(l1, 5);
    PrintL("Original             ", L1);
    ReverseList(L1);
    PrintL("ReverseList          ", L1);   // expect 5 4 3 2 1
    DestroyList(L1);

    ElemType l2[] = {1, 2, 2, 3, 2, 4};
    LinkList L2 = BuildList(l2, 6);
    DelXRecur(L2->next, 2);                // 头结点不参与判断，传 L->next
    PrintL("DelXRecur(2)         ", L2);   // expect 1 3 4
    DestroyList(L2);

    ElemType l3[] = {2, 2, 5, 2};
    LinkList L3 = BuildList(l3, 4);
    removed = DelXIter(L3, 2);
    PrintL("DelXIter(2)          ", L3);   // expect 5
    printf("  removed %d (expect 3)\n", removed);
    DestroyList(L3);

    ElemType l4[] = {1, 3, 1, 5, 3, 7};
    LinkList L4 = BuildList(l4, 6);
    removed = DelDupUnsorted(L4);
    PrintL("DelDupUnsorted       ", L4);   // expect 1 3 5 7
    printf("  removed %d (expect 2)\n", removed);
    DestroyList(L4);

    ElemType l5[] = {1, 1, 2, 2, 2, 3, 4, 4};
    LinkList L5 = BuildList(l5, 8);
    removed = DelDupSorted(L5);
    PrintL("DelDupSorted         ", L5);   // expect 1 2 3 4
    printf("  removed %d (expect 4)\n", removed);
    DestroyList(L5);

    ElemType l6[] = {10, 20, 30, 40, 50};
    LinkList L6 = BuildList(l6, 5);
    LNode *k2 = KthFromEnd(L6, 2);
    printf("KthFromEnd(2) = %d (expect 40)\n", k2 ? k2->data : -1);
    printf("KthFromEnd(5) = %d (expect 10)\n",
           KthFromEnd(L6, 5) ? KthFromEnd(L6, 5)->data : -1);
    printf("KthFromEnd(6) = %s (expect NULL)\n", KthFromEnd(L6, 6) ? "a node" : "NULL");
    DestroyList(L6);

    // 造环：尾结点 50 指回第 2 个结点 20
    LinkList L7 = BuildList(l6, 5);
    LNode *tail = NodeAt(L7, 5);
    tail->next = NodeAt(L7, 2);
    printf("\nHasCycle = %d (expect 1)\n", HasCycle(L7) != NULL);
    LNode *entry = CycleEntry(L7);
    printf("CycleEntry = %d (expect 20)\n", entry ? entry->data : -1);
    printf("(a cycle of length 4, not 5: the head node is outside)\n");
    tail->next = NULL;                     // 断环，否则 Destroy 会死循环
    printf("HasCycle after cut = %d (expect 0)\n", HasCycle(L7) != NULL);
    DestroyList(L7);

    // 公共结点：L9 = 7 8 30 40 50，与 L8 共享后半段
    LinkList L8 = BuildList(l6, 5);        // 10 20 30 40 50
    ElemType l9[] = {7, 8};
    LinkList L9 = BuildList(l9, 2);
    NodeAt(L9, 2)->next = NodeAt(L8, 3);   // 接到 30
    LNode *common = FirstCommonNode(L8, L9);
    printf("\nFirstCommonNode = %d (expect 30)\n", common ? common->data : -1);
    NodeAt(L9, 2)->next = NULL;            // 先拆开，避免重复 free
    DestroyList(L8);
    DestroyList(L9);

    // 合并有序表
    ElemType m1[] = {1, 3, 5, 7};
    ElemType m2[] = {2, 3, 6, 8, 9};
    LinkList MA = BuildList(m1, 4);
    LinkList MB = BuildList(m2, 5);
    LinkList M = MergeSorted(MA, MB);
    printf("\n");
    PrintL("MergeSorted          ", M);   // expect 1 2 3 3 5 6 7 8 9
    DestroyList(M);

    // 拆分
    ElemType s1[] = {1, 2, 3, 4, 5, 6, 7};
    LinkList S = BuildList(s1, 7);
    LinkList SA, SB;
    SplitOddEven(S, SA, SB);
    printf("\n");
    PrintL("Split odd positions   ", SA); // expect 1 3 5 7
    PrintL("Split even positions  ", SB); // expect 2 4 6
    PrintL("Source after split    ", S);  // expect (empty)
    DestroyList(SA);
    DestroyList(SB);
    DestroyList(S);

    ElemType s2[] = {3, 1, 4, 1, 5, 9, 2, 6};
    LinkList S2 = BuildList(s2, 8);
    SplitByValue(S2, 4, SA, SB);
    printf("\n");
    PrintL("Split < 4             ", SA); // expect 3 1 1 2
    PrintL("Split >= 4            ", SB); // expect 4 5 9 6
    DestroyList(SA);
    DestroyList(SB);
    DestroyList(S2);

    // 删除区间
    ElemType d1[] = {1, 2, 3, 4, 5, 6, 7, 8};
    LinkList D = BuildList(d1, 8);
    removed = DeleteRange(D, 2, 7);
    printf("\nDeleteRange(2, 7) removed %d (expect 4)\n", removed);
    PrintL("After DeleteRange    ", D);   // expect 1 2 7 8
    DestroyList(D);

    // 重排
    ElemType r1[] = {1, 2, 3, 4, 5, 6, 7};
    LinkList R = BuildList(r1, 7);
    ReorderList(R);
    printf("\n");
    PrintL("Reorder n=7          ", R);   // expect 1 7 2 6 3 5 4
    DestroyList(R);

    ElemType r2[] = {1, 2, 3, 4};
    R = BuildList(r2, 4);
    ReorderList(R);
    PrintL("Reorder n=4          ", R);   // expect 1 4 2 3
    DestroyList(R);

    ElemType r3[] = {1};
    R = BuildList(r3, 1);
    ReorderList(R);
    PrintL("Reorder n=1          ", R);   // expect 1
    DestroyList(R);

    return 0;
}
