! ABI-preserving compact/expanded vorticity-divergence storage adapters.
!
! The external F2PY-facing symbols ``onedtotwod_vrtdiv`` and
! ``twodtooned_vrtdiv`` are kept below. Their implementations use explicit
! modern interfaces while preserving compact triangular storage, signs and the
! historical 0.5 scaling for all physically defined degrees.
module spharm_vector_spectral_storage
  use spharm_kinds, only : int32, real32
  implicit none
  private

  public :: expand_vorticity_divergence_spectra
  public :: compact_vorticity_divergence_spectra

contains

  pure integer(int32) function triangular_truncation(nmdim) result(ntrunc)
    ! Return the compact triangular truncation implied by ``nmdim``.
    integer(int32), intent(in) :: nmdim

    ntrunc = 0_int32
    do while (((ntrunc + 2_int32) * (ntrunc + 3_int32)) / 2_int32 <= nmdim)
      ntrunc = ntrunc + 1_int32
    end do
  end function triangular_truncation


  subroutine expand_vorticity_divergence_spectra( &
      vrtspec, divspec, br, bi, cr, ci, nlat, nmdim, nt, rsphere)
    ! Expand compact vorticity/divergence coefficients to vector-harmonic
    ! triangular arrays. The total-degree-zero mode is physically undefined
    ! for both vorticity and divergence and is represented as zero.
    integer(int32), intent(in) :: nlat
    integer(int32), intent(in) :: nmdim
    integer(int32), intent(in) :: nt
    complex(real32), intent(in) :: vrtspec(nmdim, nt)
    complex(real32), intent(in) :: divspec(nmdim, nt)
    real(real32), intent(out) :: br(nlat, nlat, nt)
    real(real32), intent(out) :: bi(nlat, nlat, nt)
    real(real32), intent(out) :: cr(nlat, nlat, nt)
    real(real32), intent(out) :: ci(nlat, nlat, nt)
    real(real32), intent(in) :: rsphere

    integer(int32) :: coefficient_index
    integer(int32) :: compact_start
    integer(int32) :: field_index
    integer(int32) :: ntrunc
    integer(int32) :: total_degree
    integer(int32) :: zonal_degree
    real(real32) :: degree_factor
    real(real32), parameter :: scale = 0.5_real32

    ntrunc = triangular_truncation(nmdim)

    do field_index = 1_int32, nt
      compact_start = 0_int32
      do zonal_degree = 0_int32, ntrunc
        do total_degree = zonal_degree, ntrunc
          coefficient_index = compact_start + total_degree - zonal_degree + 1_int32

          if (total_degree == 0_int32) then
            br(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = 0.0_real32
            bi(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = 0.0_real32
            cr(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = 0.0_real32
            ci(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = 0.0_real32
          else
            degree_factor = sqrt(real(total_degree * (total_degree + 1_int32), real32))
            br(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = &
              -(rsphere / degree_factor) * &
              real(divspec(coefficient_index, field_index) / scale, kind=real32)
            bi(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = &
              -(rsphere / degree_factor) * &
              aimag(divspec(coefficient_index, field_index) / scale)
            cr(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = &
              (rsphere / degree_factor) * &
              real(vrtspec(coefficient_index, field_index) / scale, kind=real32)
            ci(zonal_degree + 1_int32, total_degree + 1_int32, field_index) = &
              (rsphere / degree_factor) * &
              aimag(vrtspec(coefficient_index, field_index) / scale)
          end if
        end do
        compact_start = compact_start + ntrunc - zonal_degree + 1_int32
      end do
    end do
  end subroutine expand_vorticity_divergence_spectra


  subroutine compact_vorticity_divergence_spectra( &
      vrtspec, divspec, br, bi, cr, ci, nlat, ntrunc, nt, rsphere)
    ! Compact vector-harmonic triangular arrays into vorticity/divergence
    ! coefficients. The total-degree-zero coefficients are explicitly zero.
    integer(int32), intent(in) :: nlat
    integer(int32), intent(in) :: ntrunc
    integer(int32), intent(in) :: nt
    complex(real32), intent(out) :: vrtspec((ntrunc + 1_int32) * &
                                             (ntrunc + 2_int32) / 2_int32, nt)
    complex(real32), intent(out) :: divspec((ntrunc + 1_int32) * &
                                             (ntrunc + 2_int32) / 2_int32, nt)
    real(real32), intent(in) :: br(nlat, nlat, nt)
    real(real32), intent(in) :: bi(nlat, nlat, nt)
    real(real32), intent(in) :: cr(nlat, nlat, nt)
    real(real32), intent(in) :: ci(nlat, nlat, nt)
    real(real32), intent(in) :: rsphere

    integer(int32) :: coefficient_index
    integer(int32) :: compact_start
    integer(int32) :: field_index
    integer(int32) :: total_degree
    integer(int32) :: zonal_degree
    real(real32) :: degree_factor
    real(real32), parameter :: scale = 0.5_real32

    do field_index = 1_int32, nt
      compact_start = 0_int32
      do zonal_degree = 0_int32, ntrunc
        do total_degree = zonal_degree, ntrunc
          coefficient_index = compact_start + total_degree - zonal_degree + 1_int32

          if (total_degree == 0_int32) then
            vrtspec(coefficient_index, field_index) = cmplx(0.0_real32, 0.0_real32, kind=real32)
            divspec(coefficient_index, field_index) = cmplx(0.0_real32, 0.0_real32, kind=real32)
          else
            degree_factor = sqrt(real(total_degree * (total_degree + 1_int32), real32))
            divspec(coefficient_index, field_index) = &
              -(degree_factor / rsphere) * scale * cmplx( &
                br(zonal_degree + 1_int32, total_degree + 1_int32, field_index), &
                bi(zonal_degree + 1_int32, total_degree + 1_int32, field_index), &
                kind=real32)
            vrtspec(coefficient_index, field_index) = &
              (degree_factor / rsphere) * scale * cmplx( &
                cr(zonal_degree + 1_int32, total_degree + 1_int32, field_index), &
                ci(zonal_degree + 1_int32, total_degree + 1_int32, field_index), &
                kind=real32)
          end if
        end do
        compact_start = compact_start + ntrunc - zonal_degree + 1_int32
      end do
    end do
  end subroutine compact_vorticity_divergence_spectra

end module spharm_vector_spectral_storage


subroutine onedtotwod_vrtdiv(vrtspec, divspec, br, bi, cr, ci, nlat, nmdim, nt, rsphere)
  ! External compatibility wrapper retained for F2PY and downstream callers.
  use spharm_kinds, only : int32, real32
  use spharm_vector_spectral_storage, only : expand_vorticity_divergence_spectra
  implicit none

  integer(int32), intent(in) :: nlat
  integer(int32), intent(in) :: nmdim
  integer(int32), intent(in) :: nt
  complex(real32), intent(in) :: vrtspec(nmdim, nt)
  complex(real32), intent(in) :: divspec(nmdim, nt)
  real(real32), intent(out) :: br(nlat, nlat, nt)
  real(real32), intent(out) :: bi(nlat, nlat, nt)
  real(real32), intent(out) :: cr(nlat, nlat, nt)
  real(real32), intent(out) :: ci(nlat, nlat, nt)
  real(real32), intent(in) :: rsphere

  call expand_vorticity_divergence_spectra( &
    vrtspec, divspec, br, bi, cr, ci, nlat, nmdim, nt, rsphere)
end subroutine onedtotwod_vrtdiv


subroutine twodtooned_vrtdiv(vrtspec, divspec, br, bi, cr, ci, nlat, ntrunc, nt, rsphere)
  ! External compatibility wrapper retained for F2PY and downstream callers.
  use spharm_kinds, only : int32, real32
  use spharm_vector_spectral_storage, only : compact_vorticity_divergence_spectra
  implicit none

  integer(int32), intent(in) :: nlat
  integer(int32), intent(in) :: ntrunc
  integer(int32), intent(in) :: nt
  complex(real32), intent(out) :: vrtspec((ntrunc + 1_int32) * &
                                           (ntrunc + 2_int32) / 2_int32, nt)
  complex(real32), intent(out) :: divspec((ntrunc + 1_int32) * &
                                           (ntrunc + 2_int32) / 2_int32, nt)
  real(real32), intent(in) :: br(nlat, nlat, nt)
  real(real32), intent(in) :: bi(nlat, nlat, nt)
  real(real32), intent(in) :: cr(nlat, nlat, nt)
  real(real32), intent(in) :: ci(nlat, nlat, nt)
  real(real32), intent(in) :: rsphere

  call compact_vorticity_divergence_spectra( &
    vrtspec, divspec, br, bi, cr, ci, nlat, ntrunc, nt, rsphere)
end subroutine twodtooned_vrtdiv
