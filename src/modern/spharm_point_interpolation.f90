! ABI-preserving pointwise spectral interpolation adapters.
!
! The external F2PY-facing symbols ``getlegfunc`` and ``specintrp`` are kept
! below. Their implementations use explicit modern interfaces and retain the
! established single-precision numerical kernels ``alfk`` and ``lfpt``.
module spharm_point_interpolation
  use spharm_kinds, only : int32, real32
  use spharm_legacy_interfaces, only : alfk, lfpt
  implicit none
  private

  public :: evaluate_associated_legendre
  public :: interpolate_scalar_spectrum

contains

  subroutine evaluate_associated_legendre(legfunc, lat, ntrunc)
    ! Evaluate normalized associated Legendre values in compact triangular order.
    integer(int32), intent(in) :: ntrunc
    real(real32), intent(in) :: lat
    real(real32), intent(out) :: legfunc((ntrunc + 1_int32) * (ntrunc + 2_int32) / 2_int32)

    integer(int32) :: coefficient_index
    integer(int32) :: nm_start
    integer(int32) :: total_degree
    integer(int32) :: zonal_degree
    real(real32) :: cp((ntrunc / 2_int32) + 1_int32)
    real(real32) :: pi
    real(real32) :: theta

    ! Keep the historical single-precision conversion and colatitude formula.
    pi = 4.0_real32 * atan(1.0_real32)
    theta = 0.5_real32 * pi - (pi / 180.0_real32) * lat

    nm_start = 0_int32
    do zonal_degree = 0_int32, ntrunc
      do total_degree = zonal_degree, ntrunc
        coefficient_index = nm_start + total_degree - zonal_degree + 1_int32
        call alfk(total_degree, zonal_degree, cp)
        call lfpt(total_degree, zonal_degree, theta, cp, legfunc(coefficient_index))
      end do
      nm_start = nm_start + ntrunc - zonal_degree + 1_int32
    end do
  end subroutine evaluate_associated_legendre


  subroutine interpolate_scalar_spectrum(rlon, ntrunc, datnm, scrm, pnm, ob)
    ! Synthesize one scalar value from compact coefficients at longitude rlon.
    integer(int32), intent(in) :: ntrunc
    real(real32), intent(in) :: rlon
    complex(real32), intent(in) :: datnm((ntrunc + 1_int32) * (ntrunc + 2_int32) / 2_int32)
    complex(real32), intent(out) :: scrm(ntrunc + 1_int32)
    real(real32), intent(in) :: pnm((ntrunc + 1_int32) * (ntrunc + 2_int32) / 2_int32)
    real(real32), intent(out) :: ob

    integer(int32) :: coefficient_index
    integer(int32) :: nm_start
    integer(int32) :: total_degree
    integer(int32) :: zonal_degree
    integer(int32) :: mwaves

    mwaves = ntrunc + 1_int32
    nm_start = 0_int32

    do zonal_degree = 0_int32, ntrunc
      scrm(zonal_degree + 1_int32) = cmplx(0.0_real32, 0.0_real32, kind=real32)
      do total_degree = zonal_degree, ntrunc
        coefficient_index = nm_start + total_degree - zonal_degree + 1_int32
        scrm(zonal_degree + 1_int32) = scrm(zonal_degree + 1_int32) + &
          datnm(coefficient_index) * pnm(coefficient_index)
      end do
      nm_start = nm_start + mwaves - zonal_degree
    end do

    ! Assignment of a complex value to the historical REAL output retained its
    ! real component. Express that conversion explicitly in modern Fortran.
    ob = real(scrm(1), kind=real32)
    do zonal_degree = 1_int32, ntrunc
      ob = ob + 2.0_real32 * real(scrm(zonal_degree + 1_int32), kind=real32) * &
        cos(real(zonal_degree, real32) * rlon) - &
        2.0_real32 * aimag(scrm(zonal_degree + 1_int32)) * &
        sin(real(zonal_degree, real32) * rlon)
    end do
  end subroutine interpolate_scalar_spectrum

end module spharm_point_interpolation


subroutine getlegfunc(legfunc, lat, ntrunc)
  ! External compatibility wrapper retained for F2PY and downstream callers.
  use spharm_kinds, only : int32, real32
  use spharm_point_interpolation, only : evaluate_associated_legendre
  implicit none

  integer(int32), intent(in) :: ntrunc
  real(real32), intent(in) :: lat
  real(real32), intent(out) :: legfunc((ntrunc + 1_int32) * (ntrunc + 2_int32) / 2_int32)

  call evaluate_associated_legendre(legfunc, lat, ntrunc)
end subroutine getlegfunc


subroutine specintrp(rlon, ntrunc, datnm, scrm, pnm, ob)
  ! External compatibility wrapper retained for F2PY and downstream callers.
  use spharm_kinds, only : int32, real32
  use spharm_point_interpolation, only : interpolate_scalar_spectrum
  implicit none

  integer(int32), intent(in) :: ntrunc
  real(real32), intent(in) :: rlon
  complex(real32), intent(in) :: datnm((ntrunc + 1_int32) * (ntrunc + 2_int32) / 2_int32)
  complex(real32), intent(out) :: scrm(ntrunc + 1_int32)
  real(real32), intent(in) :: pnm((ntrunc + 1_int32) * (ntrunc + 2_int32) / 2_int32)
  real(real32), intent(out) :: ob

  call interpolate_scalar_spectrum(rlon, ntrunc, datnm, scrm, pnm, ob)
end subroutine specintrp
