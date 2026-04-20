---
title: Fortran-01-Hello World!
date: 2026-03-30 22:56:17
published: false
tags:
---

Fortran是一门编译型的编程语言，特长是科学计算，教程：

1. [Fortran语言实践](https://fortran-lang.org/zh_CN/learn/best_practices/)
2. [现代Fortran程序设计](https://fortran-fans.github.io/Modern-Fortran-Programming/)
3. https://github.com/zang-langyan/Fortran-Tutorial-CN

### 变量

基本数据类型：integer整数、real实数、comples复数、character字符、logical逻辑值；Fortran 是一种**静态类型语言**，这意味着每个变量的类型在程序编译时是固定的 —— 变量类型在程序运行时不能改变。

声明变量的语法：

```
<variable_type> :: <variable_name>, <variable_name>, ...
```

程序开头的附加语句：`implicit none`，该语句告诉编译器所有变量都将被显式声明；如果没有此语句，变量将根据它们开头的字母隐式键入。

字符由单引号 (`'`) 或双引号 (`"`) 包围，逻辑或布尔值可以是 `.true.` 或 `.false.`。

### 基本运算

Fortran不区分大小写，每一个`program` 或 `subroutine` 或 `function` 中必须在开头先声明所有需要使用的变量，不可以在主体运算部分另起声明。

```fortran
program variable
   implicit none

   integer::r
   real::pi
   real::s
   complex::z
   character::char
   logical::isokey

   r=5
   pi=3.1415
   s=pi*r*r
   z = (1.0, -0.5) ! 1.0 - 0.5i
   char='A'

   print*,(s)
   print*,(char)

end program variable

```

浮点数精度：32位和64位，没有声明类型时一般为32位。

`parameter` 代表常量，在运行过程中无法修改，类似于C/C++中的`const`，所以需要在声明时初始化：

```fortran
program molar_mass
  implicit none

  real, parameter :: NaCl = 58.5 ! 氯化钠的摩尔质量为58.5g/mol
  real :: mass
  real :: mol

  print *, '输入氯化钠质量:'
  read(*,*) mass

  mol = mass / NaCl

  print *, 'NaCl'
  print *, '摩尔量为: ', mol, ' mol'

end program molar_mass
```

### 数组

声明数组变量有两种常见的表示法：使用 `dimension` 属性或通过将括号中的数组维度附加到变量名称，Fortran 数组以 *column-major* 顺序存储。

**数组默认从1开始序数**，也可以自定义从任意位置开始序数，多维数组由前向后（维度）记录 (column major)。

数组切片是个“开区间”。

```fortran
   ! 数组的两种定义方法
   integer,dimension(5)::array1
   integer::array2(10)
   integer::i
  
   ! 数组的初始化方法
   array1=[1,2,3,4,5]
   !array2=[1,2,3,4,5,6,7,8,9,10]
   array2=[(i,i=1,10)]
   array2(6:)=99

   ! 数组切片
   !print*,array1(2:3)
   print*,array2(3:9:2)
   print*,array2(10:1:-1)
   print*,array2(7:2:-1)
```

在程序中指定数组大小的称为**静态数组**，其大小在编译程序时是固定的，而**可分配动态数组**需要 `allocatable` 数组。

```fortran
  integer, allocatable :: array1(:)
  integer, allocatable :: array2(:,:)

  allocate(array1(10))
  allocate(array2(10,10))

  ! ...

  deallocate(array1)
  deallocate(array2)
```

### 字符串数组



```fortran
program string
   implicit none

   !定长字符串
   character(len=5)::name
   !变长字符串
   character(:),allocatable::college
   !字符串数组
   character(10),dimension(3,2)::keys
   keys(1,:)=[character(len=10)::"hello","world"]
   keys(2,:)=[character(len=10)::"good","morning"]
   keys(3,:)=[character(len=10)::"how are","you"]
   name="xxx,"

   call show(name,keys)

   !print*,keys
   contains
   subroutine show(k,v)
      character(len=*),intent(in)::k,v(:,:)
      integer::i
      print*,k
      
      do i=1,size(v,1)
         print*,v(i,:)
      end do
   end subroutine show

end program string
```







