! ABI-preserving geodesic point coordinate generator.
!
! The external F2PY-facing symbol ``ihgeod`` is retained below. The
! implementation follows the historical unfolded-icosahedron construction,
! but uses explicit kinds, intents, and helper procedures.
module spharm_geodesic
  use spharm_kinds, only : int32, real32
  implicit none
  private

  public :: generate_geodesic_coordinates

contains

  subroutine spherical_to_cartesian(radius, theta, phi, x, y, z)
    real(real32), intent(in) :: radius
    real(real32), intent(in) :: theta
    real(real32), intent(in) :: phi
    real(real32), intent(out) :: x
    real(real32), intent(out) :: y
    real(real32), intent(out) :: z

    real(real32) :: sine_theta

    sine_theta = sin(theta)
    x = radius * sine_theta * cos(phi)
    y = radius * sine_theta * sin(phi)
    z = radius * cos(theta)
  end subroutine spherical_to_cartesian


  subroutine cartesian_to_spherical(x, y, z, radius, theta, phi)
    real(real32), intent(in) :: x
    real(real32), intent(in) :: y
    real(real32), intent(in) :: z
    real(real32), intent(out) :: radius
    real(real32), intent(out) :: theta
    real(real32), intent(out) :: phi

    real(real32) :: horizontal_radius
    real(real32) :: pi

    pi = 4.0_real32 * atan(1.0_real32)
    horizontal_radius = x * x + y * y

    if (horizontal_radius /= 0.0_real32) then
      radius = sqrt(horizontal_radius + z * z)
      horizontal_radius = sqrt(horizontal_radius)
      phi = atan2(y, x)
      theta = atan2(horizontal_radius, z)
    else
      radius = abs(z)
      phi = 0.0_real32
      theta = 0.0_real32
      if (z < 0.0_real32) theta = pi
    end if
  end subroutine cartesian_to_spherical


  subroutine normalize_unit_sphere(x, y, z, idp, jdp)
    integer(int32), intent(in) :: idp
    integer(int32), intent(in) :: jdp
    real(real32), intent(inout) :: x(idp, jdp, 5)
    real(real32), intent(inout) :: y(idp, jdp, 5)
    real(real32), intent(inout) :: z(idp, jdp, 5)

    integer(int32) :: i
    integer(int32) :: j
    integer(int32) :: k
    real(real32) :: phi
    real(real32) :: radius
    real(real32) :: theta

    do k = 1_int32, 5_int32
      do j = 1_int32, idp
        do i = 1_int32, jdp
          call cartesian_to_spherical(x(j, i, k), y(j, i, k), z(j, i, k), radius, theta, phi)
          call spherical_to_cartesian(1.0_real32, theta, phi, x(j, i, k), y(j, i, k), z(j, i, k))
        end do
      end do
    end do
  end subroutine normalize_unit_sphere


  subroutine generate_geodesic_coordinates(edge_points, x, y, z, idp, jdp)
    integer(int32), intent(in) :: edge_points
    integer(int32), intent(in) :: idp
    integer(int32), intent(in) :: jdp
    real(real32), intent(out) :: x(idp, jdp, 5)
    real(real32), intent(out) :: y(idp, jdp, 5)
    real(real32), intent(out) :: z(idp, jdp, 5)

    integer(int32) :: i
    integer(int32) :: j
    integer(int32) :: k
    real(real32) :: beta
    real(real32) :: dphi
    real(real32) :: dx_i
    real(real32) :: dx_j
    real(real32) :: dy_i
    real(real32) :: dy_j
    real(real32) :: dz_i
    real(real32) :: dz_j
    real(real32) :: half_dphi
    real(real32) :: phi
    real(real32) :: pi
    real(real32) :: theta1
    real(real32) :: theta2
    real(real32) :: three_half_dphi
    real(real32) :: x1, x2, x3, x4, x5, x6
    real(real32) :: xs
    real(real32) :: y1, y2, y3, y4, y5, y6
    real(real32) :: ys
    real(real32) :: z1, z2, z3, z4, z5, z6
    real(real32) :: zs
    real(real32) :: spacing

    x = 0.0_real32
    y = 0.0_real32
    z = 0.0_real32

    if (edge_points <= 1_int32) return

    pi = 4.0_real32 * atan(1.0_real32)
    dphi = 0.4_real32 * pi
    beta = cos(dphi)
    theta1 = acos(beta / (1.0_real32 - beta))
    theta2 = pi - theta1
    half_dphi = dphi / 2.0_real32
    three_half_dphi = 3.0_real32 * half_dphi
    spacing = real(edge_points - 1_int32, real32)

    do k = 1_int32, 5_int32
      phi = real(k - 1_int32, real32) * dphi

      call spherical_to_cartesian(1.0_real32, theta2, phi, x1, y1, z1)
      call spherical_to_cartesian(1.0_real32, pi, phi + half_dphi, x2, y2, z2)
      call spherical_to_cartesian(1.0_real32, theta2, phi + dphi, x3, y3, z3)

      dx_i = (x2 - x1) / spacing
      dy_i = (y2 - y1) / spacing
      dz_i = (z2 - z1) / spacing
      dx_j = (x3 - x2) / spacing
      dy_j = (y3 - y2) / spacing
      dz_j = (z3 - z2) / spacing

      do i = 1_int32, edge_points
        xs = x1 + real(i - 1_int32, real32) * dx_i
        ys = y1 + real(i - 1_int32, real32) * dy_i
        zs = z1 + real(i - 1_int32, real32) * dz_i
        do j = 1_int32, i
          x(j, i, k) = xs + real(j - 1_int32, real32) * dx_j
          y(j, i, k) = ys + real(j - 1_int32, real32) * dy_j
          z(j, i, k) = zs + real(j - 1_int32, real32) * dz_j
        end do
      end do

      call spherical_to_cartesian(1.0_real32, theta1, phi + half_dphi, x4, y4, z4)

      dx_i = (x3 - x4) / spacing
      dy_i = (y3 - y4) / spacing
      dz_i = (z3 - z4) / spacing
      dx_j = (x4 - x1) / spacing
      dy_j = (y4 - y1) / spacing
      dz_j = (z4 - z1) / spacing

      do j = 1_int32, edge_points
        xs = x1 + real(j - 1_int32, real32) * dx_j
        ys = y1 + real(j - 1_int32, real32) * dy_j
        zs = z1 + real(j - 1_int32, real32) * dz_j
        do i = 1_int32, j
          x(j, i, k) = xs + real(i - 1_int32, real32) * dx_i
          y(j, i, k) = ys + real(i - 1_int32, real32) * dy_i
          z(j, i, k) = zs + real(i - 1_int32, real32) * dz_i
        end do
      end do

      call spherical_to_cartesian(1.0_real32, theta1, phi + three_half_dphi, x5, y5, z5)

      dx_j = (x5 - x3) / spacing
      dy_j = (y5 - y3) / spacing
      dz_j = (z5 - z3) / spacing

      do i = 1_int32, edge_points
        xs = x4 + real(i - 1_int32, real32) * dx_i
        ys = y4 + real(i - 1_int32, real32) * dy_i
        zs = z4 + real(i - 1_int32, real32) * dz_i
        do j = 1_int32, i
          x(j + edge_points - 1_int32, i, k) = xs + real(j - 1_int32, real32) * dx_j
          y(j + edge_points - 1_int32, i, k) = ys + real(j - 1_int32, real32) * dy_j
          z(j + edge_points - 1_int32, i, k) = zs + real(j - 1_int32, real32) * dz_j
        end do
      end do

      call spherical_to_cartesian(1.0_real32, 0.0_real32, phi + dphi, x6, y6, z6)

      dx_i = (x5 - x6) / spacing
      dy_i = (y5 - y6) / spacing
      dz_i = (z5 - z6) / spacing
      dx_j = (x6 - x4) / spacing
      dy_j = (y6 - y4) / spacing
      dz_j = (z6 - z4) / spacing

      do j = 1_int32, edge_points
        xs = x4 + real(j - 1_int32, real32) * dx_j
        ys = y4 + real(j - 1_int32, real32) * dy_j
        zs = z4 + real(j - 1_int32, real32) * dz_j
        do i = 1_int32, j
          x(j + edge_points - 1_int32, i, k) = xs + real(i - 1_int32, real32) * dx_i
          y(j + edge_points - 1_int32, i, k) = ys + real(i - 1_int32, real32) * dy_i
          z(j + edge_points - 1_int32, i, k) = zs + real(i - 1_int32, real32) * dz_i
        end do
      end do
    end do

    call normalize_unit_sphere(x, y, z, idp, jdp)
  end subroutine generate_geodesic_coordinates

end module spharm_geodesic


subroutine ihgeod(m, idp, jdp, x, y, z)
  ! External compatibility wrapper retained for F2PY and downstream callers.
  use spharm_kinds, only : int32, real32
  use spharm_geodesic, only : generate_geodesic_coordinates
  implicit none

  integer(int32), intent(in) :: m
  integer(int32), intent(in) :: idp
  integer(int32), intent(in) :: jdp
  real(real32), intent(out) :: x(idp, jdp, 5)
  real(real32), intent(out) :: y(idp, jdp, 5)
  real(real32), intent(out) :: z(idp, jdp, 5)

  call generate_geodesic_coordinates(m, x, y, z, idp, jdp)
end subroutine ihgeod
