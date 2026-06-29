! ABI-preserving compact/expanded scalar spectral-storage adapters.
!
! The external F2PY-facing symbols ``onedtotwod`` and ``twodtooned`` are kept
! below. Their implementations use explicit modern interfaces while preserving
! the historical compact triangular ordering and 0.5 scaling convention.
module spharm_spectral_storage
  use spharm_kinds, only : int32, real32
  implicit none
  private

  public :: expand_scalar_spectrum
  public :: compact_scalar_spectrum

contains

  pure integer(int32) function triangular_truncation(nmdim) result(ntrunc)
    ! Return the compact triangular truncation implied by ``nmdim``.
    integer(int32), intent(in) :: nmdim

    ntrunc = 0_int32
    do while (((ntrunc + 2_int32) * (ntrunc + 3_int32)) / 2_int32 <= nmdim)
      ntrunc = ntrunc + 1_int32
    end do
  end function triangular_truncation


  subroutine expand_scalar_spectrum(dataspec, a, b, nlat, nmdim, nt)
    ! Expand compact complex coefficients to the historical real/imaginary
    ! triangular matrices. Entries outside the triangular domain remain outside
    ! this routine's contract, matching the original F77 implementation.
    integer(int32), intent(in) :: nlat
    integer(int32), intent(in) :: nmdim
    integer(int32), intent(in) :: nt
    complex(real32), intent(in) :: dataspec(nmdim, nt)
    real(real32), intent(out) :: a(nlat, nlat, nt)
    real(real32), intent(out) :: b(nlat, nlat, nt)

    integer(int32) :: coefficient_index
    integer(int32) :: compact_start
    integer(int32) :: field_index
    integer(int32) :: ntrunc
    integer(int32) :: total_degree
    integer(int32) :: zonal_degree
    real(real32), parameter :: scale = 0.5_real32

    ntrunc = triangular_truncation(nmdim)

    do field_index = 1_int32, nt
      compact_start = 0_int32
      do zonal_degree = 0_int32, ntrunc
        do total_degree = zonal_degree, ntrunc
          coefficient_index = compact_start + total_degree - zonal_degree + 1_int32
          a(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = &
            real(dataspec(coefficient_index, field_index) / scale, kind=real32)
          b(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = &
            aimag(dataspec(coefficient_index, field_index) / scale)
        end do
        compact_start = compact_start + ntrunc - zonal_degree + 1_int32
      end do
    end do
  end subroutine expand_scalar_spectrum


  subroutine compact_scalar_spectrum(dataspec, a, b, nlat, ntrunc, nt)
    ! Compact historical real/imaginary triangular matrices into coefficients.
    integer(int32), intent(in) :: nlat
    integer(int32), intent(in) :: ntrunc
    integer(int32), intent(in) :: nt
    complex(real32), intent(out) :: dataspec((ntrunc + 1_int32) * &
                                              (ntrunc + 2_int32) / 2_int32, nt)
    real(real32), intent(in) :: a(nlat, nlat, nt)
    real(real32), intent(in) :: b(nlat, nlat, nt)

    integer(int32) :: coefficient_index
    integer(int32) :: compact_start
    integer(int32) :: field_index
    integer(int32) :: total_degree
    integer(int32) :: zonal_degree
    real(real32), parameter :: scale = 0.5_real32

    do field_index = 1_int32, nt
      compact_start = 0_int32
      do zonal_degree = 0_int32, ntrunc
        do total_degree = zonal_degree, ntrunc
          coefficient_index = compact_start + total_degree - zonal_degree + 1_int32
          dataspec(coefficient_index, field_index) = scale * cmplx( &
            a(zonal_degree + 1_int32, total_degree + 1_int32, field_index), &
            b(zonal_degree + 1_int32, total_degree + 1_int32, field_index), &
            kind=real32)
        end do
        compact_start = compact_start + ntrunc - zonal_degree + 1_int32
      end do
    end do
  end subroutine compact_scalar_spectrum

end module spharm_spectral_storage


subroutine onedtotwod(dataspec, a, b, nlat, nmdim, nt)
  ! External compatibility wrapper retained for F2PY and downstream callers.
  use spharm_kinds, only : int32, real32
  use spharm_spectral_storage, only : expand_scalar_spectrum
  implicit none

  integer(int32), intent(in) :: nlat
  integer(int32), intent(in) :: nmdim
  integer(int32), intent(in) :: nt
  complex(real32), intent(in) :: dataspec(nmdim, nt)
  real(real32), intent(out) :: a(nlat, nlat, nt)
  real(real32), intent(out) :: b(nlat, nlat, nt)

  call expand_scalar_spectrum(dataspec, a, b, nlat, nmdim, nt)
end subroutine onedtotwod


subroutine twodtooned(dataspec, a, b, nlat, ntrunc, nt)
  ! External compatibility wrapper retained for F2PY and downstream callers.
  use spharm_kinds, only : int32, real32
  use spharm_spectral_storage, only : compact_scalar_spectrum
  implicit none

  integer(int32), intent(in) :: nlat
  integer(int32), intent(in) :: ntrunc
  integer(int32), intent(in) :: nt
  complex(real32), intent(out) :: dataspec((ntrunc + 1_int32) * &
                                            (ntrunc + 2_int32) / 2_int32, nt)
  real(real32), intent(in) :: a(nlat, nlat, nt)
  real(real32), intent(in) :: b(nlat, nlat, nt)

  call compact_scalar_spectrum(dataspec, a, b, nlat, ntrunc, nt)
end subroutine twodtooned
