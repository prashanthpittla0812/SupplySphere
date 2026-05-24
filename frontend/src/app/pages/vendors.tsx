import { useState, useEffect, useRef } from 'react';
import { Plus, Search, MoreVertical, Star, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { vendorsApi } from '../services/vendors-api';
import { toast } from 'sonner';

interface Vendor {
  id: string;
  name: string;
  email: string;
  phone: string;
  status: string;
  rating: number;
  totalOrders: number;
}

export function VendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [open, setOpen] = useState(false);
  const nameRef = useRef<HTMLInputElement>(null);
  const emailRef = useRef<HTMLInputElement>(null);
  const phoneRef = useRef<HTMLInputElement>(null);
  const companyRef = useRef<HTMLInputElement>(null);
  const addressRef = useRef<HTMLInputElement>(null);
  const cityRef = useRef<HTMLInputElement>(null);
  const stateRef = useRef<HTMLInputElement>(null);
  const countryRef = useRef<HTMLInputElement>(null);
  const pincodeRef = useRef<HTMLInputElement>(null);
  const [newStatus, setNewStatus] = useState('pending');

  const fetchVendors = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = searchQuery ? { search: searchQuery } : undefined;
      const response = await vendorsApi.getAll(params);
      setVendors(response.data.data);
    } catch (err) {
      setError('Failed to load vendors');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVendors();
  }, [searchQuery]);

  const handleAddVendor = async () => {
    try {
      await vendorsApi.create({
        name: nameRef.current?.value || '',
        company_name: companyRef.current?.value || nameRef.current?.value || '',
        email: emailRef.current?.value || '',
        phone: phoneRef.current?.value || '',
        address: addressRef.current?.value || 'Address pending',
        city: cityRef.current?.value || 'City',
        state: stateRef.current?.value || 'State',
        country: countryRef.current?.value || 'USA',
        pincode: pincodeRef.current?.value || '00000',
      });
      if (newStatus === 'inactive') {
        toast.info('Vendor created. Set inactive from actions after approval.');
      }
      toast.success('Vendor added successfully');
      setOpen(false);
      fetchVendors();
    } catch {
      toast.error('Failed to add vendor');
    }
  };

  if (loading && vendors.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1>Vendors</h1>
            <p className="text-muted-foreground">
              Manage your vendor relationships
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
            <h1>Vendors</h1>
            <p className="text-muted-foreground">
              Manage your vendor relationships
            </p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center p-8 gap-4">
          <p className="text-destructive">{error}</p>
          <Button onClick={fetchVendors}>Retry</Button>
        </div>
      </div>
    );
  }

  const filteredVendors = vendors.filter(vendor =>
    vendor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    vendor.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Vendors</h1>
          <p className="text-muted-foreground">
            Manage your vendor relationships
          </p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Vendor
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Vendor</DialogTitle>
              <DialogDescription>
                Enter vendor details to add them to your system
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="vendor-name">Vendor Name</Label>
                <Input id="vendor-name" ref={nameRef} placeholder="Enter vendor name" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vendor-company">Company</Label>
                <Input id="vendor-company" ref={companyRef} placeholder="Company name" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vendor-email">Email</Label>
                <Input id="vendor-email" ref={emailRef} type="email" placeholder="vendor@example.com" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vendor-phone">Phone</Label>
                <Input id="vendor-phone" ref={phoneRef} placeholder="+1-555-0100" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="vendor-city">City</Label>
                  <Input id="vendor-city" ref={cityRef} placeholder="City" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="vendor-state">State</Label>
                  <Input id="vendor-state" ref={stateRef} placeholder="State" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="vendor-country">Country</Label>
                  <Input id="vendor-country" ref={countryRef} defaultValue="USA" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="vendor-pincode">Pincode</Label>
                  <Input id="vendor-pincode" ref={pincodeRef} placeholder="00000" />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="vendor-address">Address</Label>
                <Input id="vendor-address" ref={addressRef} placeholder="Street address" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="vendor-status">Status</Label>
                <Select defaultValue="pending" onValueChange={setNewStatus}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
              <Button onClick={handleAddVendor}>Add Vendor</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>All Vendors ({filteredVendors.length})</CardTitle>
            <div className="relative w-72">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search vendors..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Rating</TableHead>
                <TableHead>Total Orders</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredVendors.map((vendor) => (
                <TableRow key={vendor.id}>
                  <TableCell>
                    <div>
                      <div>{vendor.name}</div>
                      <div className="text-muted-foreground">{vendor.email}</div>
                    </div>
                  </TableCell>
                  <TableCell>{vendor.phone}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        vendor.status === 'active' ? 'success' :
                        vendor.status === 'pending' ? 'warning' :
                        'destructive'
                      }
                    >
                      {vendor.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      {vendor.rating}
                    </div>
                  </TableCell>
                  <TableCell>{vendor.totalOrders}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" onClick={() => toast.info(`${vendor.name} selected`)}>
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
