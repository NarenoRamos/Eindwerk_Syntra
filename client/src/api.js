//const API_URL_RING = import.meta.env.VITE_API_URL

export const fetchRoutes = async (date, hour) => {
  try {
    //const response = await fetch(`${API_URL_RING}?date=${date}&hour=${hour}`);
    const response = await fetch(`/api/v1/routes?date=${date}&hour=${hour}`);

    if (!response.ok) {
      throw new Error("Failed to fetch routes");
    }

    const data = await response.json();
    return data
      .filter(route => route.path && route.path.length > 0)
      .map(route => ({
        id: route.route_id,
        path: Array.isArray(route.path[0]) ? route.path[0] : route.path,
        color: route.speed_category,
        speed: route.actual_speed,
      }));
  } catch (error) {
    console.error("Error fetching routes:", error);
    return [];
  }
};

