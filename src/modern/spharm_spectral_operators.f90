! ABI-preserving modern implementation of scalar spectral operators.
!
! The F2PY-facing external symbols remain ``lap`` and ``invlap`` below. Their
! implementations delegate to explicit module procedures so downstream Python
! and Fortran callers retain the historical ABI while this subset gains modern
! declarations, kinds and testable internal structure.
module spharm_spectral_operators
  use spharm_kinds, only : int32, real32
  implicit none
  private

  public :: apply_laplacian
  public :: apply_inverse_laplacian

contains

  pure integer(int32) function triangular_truncation(nmdim) result(ntrunc)
    ! Return the triangular truncation implied by a compact coefficient count.
    integer(int32), intent(in) :: nmdim

    ntrunc = 0_int32
    do while (((ntrunc + 2_int32) * (ntrunc + 3_int32)) / 2_int32 <= nmdim)
      ntrunc = ntrunc + 1_int32
    end do
  end function triangular_truncation


  subroutine apply_laplacian(dataspec, dataspec_lap, nmdim, nt, rsphere)
    ! Apply the scalar spherical Laplacian in compact spectral storage.
    integer(int32), intent(in) :: nmdim
    integer(int32), intent(in) :: nt
    complex(real32), intent(in) :: dataspec(nmdim, nt)
    complex(real32), intent(out) :: dataspec_lap(nmdim, nt)
    real(real32), intent(in) :: rsphere

    integer(int32) :: coefficient_index
    integer(int32) :: field_index
    integer(int32) :: nm_start
    integer(int32) :: ntrunc
    integer(int32) :: total_degree
    integer(int32) :: zonal_degree
    real(real32) :: degree_factor

    ntrunc = triangular_truncation(nmdim)

    do field_index = 1_int32, nt
      nm_start = 0_int32
      do zonal_degree = 0_int32, ntrunc
        do total_degree = zonal_degree, ntrunc
          coefficient_index = nm_start + total_degree - zonal_degree + 1_int32
          degree_factor = real(total_degree, real32) * &
                          real(total_degree + 1_int32, real32)
          dataspec_lap(coefficient_index, field_index) = &
            -(degree_factor / rsphere**2) * dataspec(coefficient_index, field_index)
        end do
        nm_start = nm_start + ntrunc - zonal_degree + 1_int32
      end do
    end do
  end subroutine apply_laplacian


  subroutine apply_inverse_laplacian(dataspec, dataspec_ilap, nmdim, nt, rsphere)
    ! Apply the inverse scalar spherical Laplacian in compact spectral storage.
    ! The global mean (total degree zero) is defined as zero, matching legacy
    ! behavior because it has no inverse Laplacian on the sphere.
    integer(int32), intent(in) :: nmdim
    integer(int32), intent(in) :: nt
    complex(real32), intent(in) :: dataspec(nmdim, nt)
    complex(real32), intent(out) :: dataspec_ilap(nmdim, nt)
    real(real32), intent(in) :: rsphere

    integer(int32) :: coefficient_index
    integer(int32) :: field_index
    integer(int32) :: nm_start
    integer(int32) :: ntrunc
    integer(int32) :: total_degree
    integer(int32) :: zonal_degree
    real(real32) :: degree_factor

    ntrunc = triangular_truncation(nmdim)
    dataspec_ilap = cmplx(0.0_real32, 0.0_real32, kind=real32)

    do field_index = 1_int32, nt
      nm_start = 0_int32
      do zonal_degree = 0_int32, ntrunc
        do total_degree = max(zonal_degree, 1_int32), ntrunc
          coefficient_index = nm_start + total_degree - zonal_degree + 1_int32
          degree_factor = real(total_degree, real32) * &
                          real(total_degree + 1_int32, real32)
          dataspec_ilap(coefficient_index, field_index) = &
            -(rsphere**2 / degree_factor) * dataspec(coefficient_index, field_index)
        end do
        nm_start = nm_start + ntrunc - zonal_degree + 1_int32
      end do
    end do
  end subroutine apply_inverse_laplacian

end module spharm_spectral_operators


subroutine lap(dataspec, dataspec_lap, nmdim, nt, rsphere)
  ! External compatibility wrapper retained for F2PY and downstream callers.
  use spharm_kinds, only : int32, real32
  use spharm_spectral_operators, only : apply_laplacian
  implicit none

  integer(int32), intent(in) :: nmdim
  integer(int32), intent(in) :: nt
  complex(real32), intent(in) :: dataspec(nmdim, nt)
  complex(real32), intent(out) :: dataspec_lap(nmdim, nt)
  real(real32), intent(in) :: rsphere

  call apply_laplacian(dataspec, dataspec_lap, nmdim, nt, rsphere)
end subroutine lap


subroutine invlap(dataspec, dataspec_ilap, nmdim, nt, rsphere)
  ! External compatibility wrapper retained for F2PY and downstream callers.
  use spharm_kinds, only : int32, real32
  use spharm_spectral_operators, only : apply_inverse_laplacian
  implicit none

  integer(int32), intent(in) :: nmdim
  integer(int32), intent(in) :: nt
  complex(real32), intent(in) :: dataspec(nmdim, nt)
  complex(real32), intent(out) :: dataspec_ilap(nmdim, nt)
  real(real32), intent(in) :: rsphere

  call apply_inverse_laplacian(dataspec, dataspec_ilap, nmdim, nt, rsphere)
end subroutine invlap
