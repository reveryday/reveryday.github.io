---
title: cpp-template
date: 2026-04-26 15:57:17
tags:
---

ptrdiff_t-指针算数：

```c++
int arr[10];
int* ptr1 = &arr[5];  // 指向第6个元素
int* ptr2 = &arr[2];  // 指向第3个元素

std::ptrdiff_t diff = ptr1 - ptr2;  // 结果为 3（ptr1比ptr2大3个位置）
std::ptrdiff_t diff2 = ptr2 - ptr1; // 结果为 -3
```

std::size_t-无符号整数类型:

```c++
std::vector<int> vec(10);
std::size_t sz = vec.size();  // vector::size() 返回 std::size_t

char arr[100];
std::size_t arr_sz = sizeof(arr);  // sizeof 操作符返回 std::size_t
```



