! Shared kind definitions for new Fortran code in pyspharm-ng.
! Legacy SPHEREPACK routines retain their original default-real ABI in Stage 3.
module spharm_kinds
  use, intrinsic :: iso_fortran_env, only : int32, real32, real64
  implicit none
  private

  public :: int32
  public :: real32
  public :: real64
end module spharm_kinds
