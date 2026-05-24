import { useState, useEffect, useRef } from 'react';
import { Plus, MapPin, MoreVertical, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { warehousesApi } from '../services/warehouses-api';
import { toast } from 'sonner';

interface Warehouse {
  id: string;
  name: string;
  location: string;
  status: string;
  currentStock: number;
  capacity: number;
}

export function WarehousesPage() {
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const nameRef = useRef<HTMLInputElement>(null);
  const codeRef = useRef<HTMLInputElement>(null);
  const addressRef = useRef<HTMLInputElement>(null);
  const cityRef = useRef<HTMLInputElement>(null);
  const stateRef = useRef<HTMLInputElement>(null);
  const countryRef = useRef<HTMLInputElement>(null);
  const pincodeRef = useRef<HTMLInputElement>(null);
  const capacityRef = useRef<HTMLInputElement>(null);

  const fetchWarehouses = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await warehousesApi.getAll();
      setWarehouses(response.data.data);
    } catch (err) {
      setError('Failed to load warehouses');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const handleAddWarehouse = async () => {
    try {
      await warehousesApi.create({
        name: nameRef.current?.value || '',
        code: codeRef.current?.value || `WH-${Date.now()}`,
        address: addressRef.current?.value || '',
        city: cityRef.current?.value || '',
        state: stateRef.current?.value || '',
        country: countryRef.current?.value || 'USA',
        pincode: pincodeRef.current?.value || '00000',
        capacity: Number(capacityRef.current?.value || 0),
      });
      toast.success('Warehouse added successfully');
      setOpen(false);
      fetchWarehouses();
    } catch {
      toast.error('Failed to add warehouse');
    }
  };

  if (loading && warehouses.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1>Warehouses</h1>
            <p className="text-muted-foreground">
              Manage your warehouse facilities
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
            <h1>Warehouses</h1>
            <p className="text-muted-foreground">
              Manage your warehouse facilities
            </p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center p-8 gap-4">
          <p className="text-destructive">{error}</p>
          <Button onClick={fetchWarehouses}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Warehouses</h1>
          <p className="text-muted-foreground">
            Manage your warehouse facilities
          </p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Warehouse
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Warehouse</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="warehouse-name">Name</Label>
                  <Input id="warehouse-name" ref={nameRef} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="warehouse-code">Code</Label>
                  <Input id="warehouse-code" ref={codeRef} />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="warehouse-address">Address</Label>
                <Input id="warehouse-address" ref={addressRef} />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="warehouse-city">City</Label>
                  <Input id="warehouse-city" ref={cityRef} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="warehouse-state">State</Label>
                  <Input id="warehouse-state" ref={stateRef} />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="warehouse-country">Country</Label>
                  <Input id="warehouse-country" ref={countryRef} defaultValue="USA" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="warehouse-pincode">Pincode</Label>
                  <Input id="warehouse-pincode" ref={pincodeRef} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="warehouse-capacity">Capacity</Label>
                  <Input id="warehouse-capacity" ref={capacityRef} type="number" min="0" />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button onClick={handleAddWarehouse}>Add Warehouse</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {warehouses.map((warehouse) => {
          const utilizationPercent = (warehouse.currentStock / warehouse.capacity) * 100;
          
          return (
            <Card key={warehouse.id}>
              <CardHeader className="flex flex-row items-start justify-between">
                <div className="space-y-1">
                  <CardTitle>{warehouse.name}</CardTitle>
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <MapPin className="h-3 w-3" />
                    {warehouse.location}
                  </div>
                </div>
                <Button variant="ghost" size="icon" onClick={() => toast.info(`${warehouse.name} selected`)}>
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Status</span>
                  <Badge
                    variant={warehouse.status === 'operational' ? 'success' : 'warning'}
                  >
                    {warehouse.status}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Capacity</span>
                    <span>
                      {warehouse.currentStock.toLocaleString()} / {warehouse.capacity.toLocaleString()}
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${utilizationPercent}%` }}
                    />
                  </div>
                  <div className="text-muted-foreground text-right">
                    {utilizationPercent.toFixed(0)}% utilized
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <Button variant="outline" size="sm" onClick={() => toast.info(`${warehouse.name}: ${warehouse.location}`)}>
                    View Details
                  </Button>
                  <Button size="sm" onClick={() => toast.info('Open Inventory to manage stock levels')}>
                    Manage Stock
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
