! Explicit contracts for selected external legacy kernels.
! The routines remain external symbols while higher-level adapters may move to
! modern modules without changing the F2PY ABI.
module spharm_legacy_interfaces
  use spharm_kinds, only : int32, real32
  implicit none
  private

  public :: alfk
  public :: lfpt

  interface
    subroutine alfk(n, m, cp)
      import :: int32, real32
      integer(int32), intent(in) :: n
      integer(int32), intent(in) :: m
      real(real32), intent(out) :: cp((n / 2_int32) + 1_int32)
    end subroutine alfk

    subroutine lfpt(n, m, theta, cp, pb)
      import :: int32, real32
      integer(int32), intent(in) :: n
      integer(int32), intent(in) :: m
      real(real32), intent(in) :: theta
      real(real32), intent(in) :: cp((n / 2_int32) + 1_int32)
      real(real32), intent(out) :: pb
    end subroutine lfpt
  end interface
end module spharm_legacy_interfaces
