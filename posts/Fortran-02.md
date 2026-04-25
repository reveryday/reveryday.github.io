---
title: Fortran-02
date: 2026-03-30 22:56:17
published: false
tags:
---

控制程序流有两种主要形式：

- *Conditional* (if)：根据布尔值（真或假）选择程序路径；
- *Loop*：重复一段代码多次；

### 流程控制

- 条件结构`if-else`：

  ```fortran
  if (angle < 90.0) then
    print *, 'Angle is acute'
  else
    print *, 'Angle is obtuse'
  end if
  ```

- 循环结构`do` 循环；

- 条件循环`do while`：

  ```fortran
  integer :: i
  
  i = 1
  do while (i < 11)
    print *, i
    i = i + 1
  end do
  ```

循环控制语句：`exit` 用于提前退出循环，`cycle` 会跳过循环的剩余部分并进入下一个循环。

嵌套循环控制-标签：Fortran 允许程序员对每个循环进行 *tag* 或 *name* 。

```fortran
integer :: i, j

outer_loop: do i = 1, 10
  inner_loop: do j = 1, 10
    if ((j + i) > 10) then  ! Print only pairs of i and j that add up to 10
      cycle outer_loop  ! Go to the next iteration of the outer loop
    end if
    print *, 'I=', i, ' J=', j, ' Sum=', j + i
  end do inner_loop
end do outer_loop
```

可并行化循环（`do concurrent`）:`do concurrent` 循环用于显式指定循环内部没有相互依赖关系；这通知编译器它可以使用并行化/ *SIMD* 来加速循环的执行并更清楚地传达程序员的意图。更具体地说，这意味着任何给定的循环迭代不依赖于其它循环迭代的先前执行。任何可能发生的状态变化也必须只发生在每个 `do concurrent` 循环中。