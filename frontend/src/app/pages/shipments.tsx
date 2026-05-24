import { useState, useEffect } from 'react';
import { Search, MapPin, Calendar, Truck, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { shipmentsApi } from '../services/shipments-api';
import { format } from 'date-fns';

interface Shipment {
  id: string;
  trackingNumber: string;
  orderId: string;
  carrier: string;
  status: string;
  origin: string;
  destination: string;
  estimatedDelivery: string;
  actualDelivery?: string;
}

export function ShipmentsPage() {
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchShipments = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = searchQuery ? { search: searchQuery } : undefined;
      const response = await shipmentsApi.getAll(params);
      setShipments(response.data.data);
    } catch (err) {
      setError('Failed to load shipments');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShipments();
  }, [searchQuery]);

  if (loading && shipments.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1>Shipments</h1>
            <p className="text-muted-foreground">
              Track your shipments and deliveries
            </p>
          </div>
        </div>
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1>Shipments</h1>
            <p className="text-muted-foreground">
              Track your shipments and deliveries
            </p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center p-8 gap-4">
          <p className="text-destructive">{error}</p>
          <Button onClick={fetchShipments}>Retry</Button>
        </div>
      </div>
    );
  }

  const filteredShipments = shipments.filter(shipment =>
    shipment.trackingNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
    shipment.origin.toLowerCase().includes(searchQuery.toLowerCase()) ||
    shipment.destination.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'delivered': return 'success';
      case 'in_transit': return 'default';
      case 'processing': return 'warning';
      default: return 'outline';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Shipments</h1>
          <p className="text-muted-foreground">
            Track your shipments and deliveries
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by tracking number, origin, or destination..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <div className="grid gap-6">
        {filteredShipments.map((shipment) => (
          <Card key={shipment.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="flex items-center gap-2">
                    <Truck className="h-5 w-5" />
                    {shipment.trackingNumber}
                  </CardTitle>
                  <p className="text-muted-foreground">
                    Order #{shipment.orderId} • {shipment.carrier}
                  </p>
                </div>
                <Badge variant={getStatusVariant(shipment.status)}>
                  {shipment.status.replace('_', ' ')}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <MapPin className="h-4 w-4" />
                    Origin
                  </div>
                  <div>{shipment.origin}</div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <MapPin className="h-4 w-4" />
                    Destination
                  </div>
                  <div>{shipment.destination}</div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4 pt-4 border-t">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    Estimated Delivery
                  </div>
                  <div>{format(new Date(shipment.estimatedDelivery), 'MMM dd, yyyy')}</div>
                </div>
                {shipment.actualDelivery && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Calendar className="h-4 w-4" />
                      Actual Delivery
                    </div>
                    <div>{format(new Date(shipment.actualDelivery), 'MMM dd, yyyy')}</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
