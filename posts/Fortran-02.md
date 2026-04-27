---
title: Fortran control and modularity
date: 2026-03-30 22:56:17
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

### 子程序

子程序输入参数，称为 *dummy arguments*，在子程序名称后面的括号中指定；虚拟参数类型和属性在子例程的主体中声明，就像局部变量一样。

注意声明虚拟参数时附加的 `intent` 属性；这个可选属性向编译器表示参数是“只读”（`intent(in)`）“只写”（`intent(out)`）还是“读写”（ `intent(inout)`) 在过程中。

```fortran
! Print matrix A to screen
subroutine print_matrix(n,m,A)
  implicit none
  integer, intent(in) :: n
  integer, intent(in) :: m
  real, intent(in) :: A(n, m)

  integer :: i

  do i = 1, n
    print *, A(i, 1:m)
  end do

end subroutine print_matrix
```

### 函数

```fortran
! L2 Norm of a vector
function vector_norm(n,vec) result(norm)
  implicit none
  integer, intent(in) :: n
  real, intent(in) :: vec(n)
  real :: norm

  norm = sqrt(sum(vec**2))

end function vector_norm
```

fortran中的函数必须定义并最终为返回值赋值。

### 模块

Fortran 模块包含程序、过程和其它模块可以通过 `use` 语句访问的定义。它们可以包含数据对象、类型定义、过程和接口。

- 模块允许受控范围扩展，从而明确实体访问
- 模块自动生成现代程序所需的显式接口

> 建议始终将函数和子例程放在模块中。

```fortran
module my_mod
  implicit none

  private  ! All entities are now module-private by default
  public public_var, print_matrix  ! Explicitly export public entities

  real, parameter :: public_var = 2
  integer :: private_var

contains

  ! Print matrix A to screen
  subroutine print_matrix(A)
    real, intent(in) :: A(:,:)  ! An assumed-shape dummy argument

    integer :: i

    do i = 1, size(A,1)
      print *, A(i,:)
    end do

  end subroutine print_matrix

end module my_mod
```

要在程序中 `use` 模块：

```fortran
program use_mod
  use my_mod
  implicit none

  real :: mat(10, 10)

  mat(:,:) = public_var

  call print_matrix(mat)

end program use_mod
```

显示导入列表：`use my_mod, only: public_var`，别名导入：`use my_mod, only: printMat=>print_matrix`。

> 每个模块都应该写在一个单独的 `.f90` 源文件中。模块需要在任何 `use` 它们的程序单元之前编译。





