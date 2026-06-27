! Explicit contracts for selected external legacy routines.
! The routines remain external symbols so the current F2PY ABI is unchanged.
module spharm_legacy_interfaces
  use spharm_kinds, only : real32
  implicit none
  private

  public :: getlegfunc
  public :: specintrp
  public :: lap
  public :: invlap

  interface
    subroutine getlegfunc(legfunc, lat, ntrunc)
      import :: real32
      integer, intent(in) :: ntrunc
      real(real32), intent(out) :: legfunc((ntrunc + 1) * (ntrunc + 2) / 2)
      real(real32), intent(in) :: lat
    end subroutine getlegfunc

    subroutine specintrp(rlon, ntrunc, datnm, scrm, pnm, ob)
      import :: real32
      integer, intent(in) :: ntrunc
      real(real32), intent(in) :: rlon
      complex(real32), intent(in) :: datnm((ntrunc + 1) * (ntrunc + 2) / 2)
      complex(real32), intent(inout) :: scrm(ntrunc + 1)
      real(real32), intent(in) :: pnm((ntrunc + 1) * (ntrunc + 2) / 2)
      real(real32), intent(out) :: ob
    end subroutine specintrp

    subroutine lap(dataspec, dataspec_lap, nmdim, nt, rsphere)
      import :: real32
      integer, intent(in) :: nmdim
      integer, intent(in) :: nt
      complex(real32), intent(in) :: dataspec(nmdim, nt)
      complex(real32), intent(out) :: dataspec_lap(nmdim, nt)
      real(real32), intent(in) :: rsphere
    end subroutine lap

    subroutine invlap(dataspec, dataspec_ilap, nmdim, nt, rsphere)
      import :: real32
      integer, intent(in) :: nmdim
      integer, intent(in) :: nt
      complex(real32), intent(in) :: dataspec(nmdim, nt)
      complex(real32), intent(out) :: dataspec_ilap(nmdim, nt)
      real(real32), intent(in) :: rsphere
    end subroutine invlap
  end interface
end module spharm_legacy_interfaces
