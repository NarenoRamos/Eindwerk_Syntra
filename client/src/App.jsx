import React, { useRef, useEffect, useState } from "react";
import { MapContainer, TileLayer, Popup, Polyline} from "react-leaflet";
import { Collapse, Button, CardBody, Card, CardTitle, Form, FormGroup, Label, Input } from 'reactstrap';

import 'bootstrap/dist/css/bootstrap.min.css';
import "./App.css";

import { fetchRoutes } from "./utils/api";

const App = (args) => {
  const position = [51.2223, 4.3960];
  const [routes, setRoutes] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [hour, setHour] = useState(12); 
  const [date, setDate] = useState(""); 
  const [vehicleClass, setvehicleClass] = useState(2);
  
  const intervalRef = useRef(null);
  const toggle = () => setIsOpen(!isOpen);


  useEffect(() => {
    const getRoutes = async () => {
      const newRoutes = await fetchRoutes(vehicleClass, date, hour);
      setRoutes(newRoutes);
    };
  
    getRoutes(); // Haal direct data op bij verandering
  
    // Voorkom meerdere intervallen
    if (intervalRef.current) clearInterval(intervalRef.current);
  
    intervalRef.current = setInterval(getRoutes, 60000);
  
    return () => clearInterval(intervalRef.current); // Cleanup interval bij unmount
  }, [vehicleClass, date, hour]);
  
  return (
    <div>
      <MapContainer center={position} zoom={13} scrollWheelZoom={true}>
        
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />

        {routes.map((route) => (
          <Polyline
          key={`${route.id}-${Date.now()}`}
          positions={route.path}
          color={route.color}
          weight={3}
        >
          <Popup>
            <div>
              <h4>Gemiddelde snelheid: {route.speed} km/h</h4>
            </div>
          </Popup>
        </Polyline>
        ))}
      </MapContainer>

      <div className="input-form-container">
          <Button className="colapse-button" color="primary" onClick={toggle}>
            Analyse
          </Button>
          <Collapse isOpen={isOpen} {...args}>
            <Card className="input-card">
              <CardBody>
                <CardTitle tag="h5">
                  Analisis Tool 
                </CardTitle>
                <Form>
                <FormGroup>
                  <Label for="exampleSelect">
                    Vehicle Class
                  </Label>
                  <Input id="exampleSelect" name="select" type="select" value={vehicleClass} onChange={(e) => setvehicleClass(e.target.value)}>
                  <option value={2}>
                    2 - Passenger cars
                  </option>
                  <option value={3}>
                    3 - Delivery vans
                  </option>
                  <option value={4}>
                    4 - Rigid trucks
                  </option>
                  <option value={5}>
                    5 - Articulated trucks or buses
                  </option>
                  </Input>
                </FormGroup>
                  <FormGroup>
                    <Label for="exampleDate">Choose date</Label>
                    <Input id="exampleDate" name="date" placeholder="date placeholder" type="date" value={date} onChange={(e) => setDate(e.target.value)}/>
                  </FormGroup>
                  <FormGroup>
                    <Label for="exampleRange">Hour slider: {hour}</Label>
                    <Input id="exampleRange" name="range" type="range" min="0" max="23" step="1" value={hour} onChange={(e) => setHour(e.target.value)}/>
                  </FormGroup>
                </Form>
              </CardBody>
            </Card>
          </Collapse>
        </div>

    </div>
  );
};

export default App;